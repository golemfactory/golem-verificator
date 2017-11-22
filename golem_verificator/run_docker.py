#!/usr/bin/env python

import logging
import posixpath
import docker.errors

# THIS FILE IS FOR TESTS


from docker import Client
from docker.utils import kwargs_from_env


def local_client():
    """Returns an instance of docker.Client for communicating with
    local docker daemon.
    :returns docker.Client:
    """
    kwargs = kwargs_from_env(assert_hostname=False)
    kwargs["timeout"] = 600
    client = Client(**kwargs)
    return client

class DockerJob(object):
    # This dir contains static task resources.
    # Mounted read-only in the container.
    RESOURCES_DIR = "/golem/resources"

    # This dir contains task script and params file.
    # Mounted read-write in the container.
    WORK_DIR = "/golem/work"

    # All files in this dir are treated as output files after the task finishes.
    # Mounted read-write in the container.
    OUTPUT_DIR = "/golem/output"

    # Name of the script file, relative to WORK_DIR
    TASK_SCRIPT = "job.py"

    # Name of the parameters file, relative to WORK_DIR
    PARAMS_FILE = "params.py"

    running_jobs = []

    def __init__(self, image, script_src, parameters,
                 resources_dir, work_dir, output_dir,
                 host_config=None, container_log_level=None):
        """
        :param DockerImage image: Docker image to use
        :param str script_src: source of the task script file
        :param dict parameters: parameters for the task script
        :param str resources_dir: directory with task resources
        :param str work_dir: directory for temporary work files
        :param str output_dir: directory for output files
        """
        from golem.docker.image import DockerImage
        if not isinstance(image, DockerImage):
            raise TypeError('Incorrect image type: {}. Should be: DockerImage'.format(type(image)))
        self.image = image
        self.script_src = script_src
        self.parameters = parameters if parameters else {}
        self.host_config = host_config or {}

        self.resources_dir = resources_dir
        self.work_dir = work_dir
        self.output_dir = output_dir

        self.resources_dir_mod = None
        self.work_dir_mod = None
        self.output_dir_mod = None

        self.container = None
        self.container_id = None
        self.container_log = None
        self.state = self.STATE_NEW

        if container_log_level is None:
            container_log_level = container_logger.getEffectiveLevel()
        self.log_std_streams = 0 < container_log_level <= logging.DEBUG
        self.logging_thread = None

    @staticmethod
    def _get_container_script_path():
        return posixpath.join(DockerJob.WORK_DIR, DockerJob.TASK_SCRIPT)

    def _prepare(self):
        self.work_dir_mod = self._host_dir_chmod(self.work_dir, "rw")
        self.resources_dir_mod = self._host_dir_chmod(self.resources_dir, "rw")
        self.output_dir_mod = self._host_dir_chmod(self.output_dir, "rw")

        # Save parameters in work_dir/PARAMS_FILE
        params_file_path = self._get_host_params_path()
        with open(params_file_path, "wb") as params_file:
            for key, value in self.parameters.items():
                line = "{} = {}\n".format(key, repr(value))
                params_file.write(bytearray(line, encoding='utf-8'))

        # Save the script in work_dir/TASK_SCRIPT
        task_script_path = self._get_host_script_path()
        with open(task_script_path, "wb") as script_file:
            script_file.write(bytearray(self.script_src, "utf-8"))

        # Setup volumes for the container
        client = local_client()

        # # Docker config requires binds to be specified using posix paths,
        # # even on Windows. Hence this function:
        # def posix_path(path):
        #     if is_windows():
        #         return nt_path_to_posix_path(path)
        #     return path
        #
        # container_config = dict(self.host_config)
        # cpuset = container_config.pop('cpuset', None)
        #
        # if is_windows():
        #     environment = None
        # elif is_osx():
        #     environment = dict(OSX_USER=1)
        # else:
        #     environment = dict(LOCAL_USER_ID=os.getuid())

        # host_cfg = client.create_host_config(
        #     binds={
        #         posix_path(self.work_dir): {
        #             "bind": self.WORK_DIR,
        #             "mode": "rw"
        #         },
        #         posix_path(self.resources_dir): {
        #             "bind": self.RESOURCES_DIR,
        #             "mode": "ro"
        #         },
        #         posix_path(self.output_dir): {
        #             "bind": self.OUTPUT_DIR,
        #             "mode": "rw"
        #         }
        #     },
        #     **container_config
        # )

        # The location of the task script when mounted in the container
        container_script_path = self._get_container_script_path()
        self.container = client.create_container(
            image=self.image.name,
            volumes=[self.WORK_DIR, self.RESOURCES_DIR, self.OUTPUT_DIR],
            # host_config=host_cfg,
            command=[container_script_path],
            working_dir=self.WORK_DIR,
            # cpuset=cpuset,
            # environment=environment
        )
        self.container_id = self.container["Id"]
        if self.container_id is None:
            raise KeyError("container does not have key: Id")

        self.running_jobs.append(self)
        logger.debug("Container {} prepared, image: {}, dirs: {}; {}; {}"
                     .format(self.container_id, self.image.name,
                             self.work_dir, self.resources_dir, self.output_dir)
                     )
