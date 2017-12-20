[![CircleCI](https://circleci.com/gh/golemfactory/golem-verificator.svg?style=shield)](https://circleci.com/gh/golemfactory/golem-verificator)

# golem-verificator
 Shared module for verification (Golem &amp; Concent)

# Example run

* In Docker_CV perform building docker container with following command
    <blockquote>docker build -t YourImageName .</blockquote>

* Run container with example data
<blockquote>docker run -d --mount type=bind,source=/path/to/images/defined/in/params/,target=/golem/resources -v /path/to/params/script/golem-verificator/tests/docker_cv_tests/files_for_tests/params.py:/golem/work/params.py YourImageName</blockquote>

By default, Golem installs latest repository version in a 'develop' mode 
(see Golem's requirements.txt)
