[![CircleCI](https://circleci.com/gh/golemfactory/golem-verificator.svg?style=shield)](https://circleci.com/gh/golemfactory/golem-verificator)

﻿Currently deploying new version of Golem Verificator is composed from three steps.

First of all, code repository is placed on Github, here:

https://github.com/golemfactory/golem-verificator

Main branch is master, verificator versions in written inside setup.py file.
Each version bump is coupled with additional tagged (master in most cases) branch.

Working with python is always best experience with virtualenvs. On linux it can be
created and activated with commands:

    python3 -m venv YourEnvName 

This will create virtualenv and activate it, if you have one, simply activate it with
 
    source PathToYourEnv/bin/activate

and deactivate it with:

    deactivate

On windows analog is:

    python3 -m venv YourEnvName
    YourEnvName\Scripts\activate.bat
    deactivate

Inside this repository, there is docker file, and all necessary resources to build
image_metrics container. This is first step.

1.  Make any necessary changes to scripts inside golem_verificator/docker/blender/images
    In particular change pkl file with current classifier. Make sure that this file
    has right permission! It should have at least read for 'others' permission. If new
    classifier has some new features, make sure that it is included in imgmetrics.py.
    Also remember that currently metrics are not available as a separate module so 
    it has to be synchronized manually.

    After code is right build docker container, launch this from 'images' directory

        docker build -t golemfactory/image_metrics:1.8 .

    This image will be build and deployed locally, you should notice the version number,
    match this accordingly to current state. This version number must be reflected in 
    blender_verifier.py::BlenderVerifier::DOCKER_TAG constant.

    After this local image will be deployed and verificator will use, the one specified in
    BlenderVerifier. However in order to use it publicly one has to publish this on docker hub.
    Simply login with given credentials, and push image.

        docker login
        docker push golemfactory/image_metrics:1.8

    After this image will be publicly available to anyone but for one more thing is necessary for golem nodes,
    so they can download it from this source. But this will be in third step. Second step.

2.  Second step is to actually prepare golem-verifictor python wheel. Verificator repository has
    necessary setup.py script which will prepare it for you. So after including all changes in code
    (most important, DOCKER_TAG), bumping up version (warning during deployment, version lower than already published
    will not be accepted) and marking this as new tag (docker push tag 0.0.0; docker push --tags)
    pack it to wheel with

        python setup.py bdist_wheel

    Note that for this to work python wheel package need to be installed in system (possibly in virtualenv).
    This will place versioned wheel in dist folder. This wheel can be installed locally (they same but without packing
    can be achieved with python setup.py install command) for test purpose. In order to be available for golem this
    wheel need to be deployed on our pypi server. This can be done with:

        ./deploy/upload.sh

    This needs that you provided valid gpg key through agent that this script can reach. GPG key need to be deployed before
    on our PYPI server, in case of doubts kindly ask Karol Tomala to do this. So the docker image is publicly available
    and wheel is available for golem. Third step.

3.  Last step is about connecting dots. First as i mentioned before in first step, golem need to know which image_metrics
    container download. This can be done changing version number in apps/images.ini.
    Next newer version of wheel with verificator needs to be specified in requirements.txt and requirements_to-freeze.txt.
    Thats all.

Tests

  It is always good to test any changes on each step. Final test is to launch two golem instances and check if everything is working
  as expected.

  First quick test can be performed after build custom container, and changing its version in blender_verifier.py and images.ini.
  Uninstall whatever verificator your golem has, and deploy custom one with:

      python setup.py install

  Check if its your desired version with:

      pip show Golem_Verificator

  When ready launch golem tests to check how new verificator is integrating with golem, most notably:

  Run this from inside golem repository, top level dir.

  For quick check

      pytest tests/apps/blender/task/test_blenderrendertask.py::TestBlenderFrameTask::test_computation_failed_or_finished
      pytest tests/golem/docker/test_docker_blender_task.py::TestDockerBlenderCyclesTask::test_blender_subtask_timeout
      pytest tests/apps/blender/test_blender_reference_generator.py

  For comprehensive check

      pytest --runslow

  First instance can be launched with:
  
      python golemapp.py --protocol_id=1337 --password=pass --datadir=/home/elfoniok/datadir3

  On the first time when datadir is created remember to accept the terms with (on second terminal)

      ./golemcli.py terms accept

  Launch second instance with:

      python golemapp.py --protocol_id=1337 --password=pass -r 127.0.0.1:61100 --peer 127.0.0.1:40102 --datadir=/home/elfoniok/datadir4

  Once again accept terms if necessary, this time for second instance

     ./golemcli.py --address 127.0.0.1 --port 61100 terms accept
