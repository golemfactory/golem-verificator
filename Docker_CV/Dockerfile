# Use an official Python runtime as a parent image
FROM python:3.6

# Install any needed packages specified in requirements.txt
RUN apt-get update \
	&& apt-get install -y 

RUN apt-get install -y software-properties-common \
	&& apt-get update \
	&& apt-get install -y python3-pip

RUN mkdir -v /golem \
 && mkdir -v /golem/work \
 && mkdir -v /golem/resources \
 && mkdir -v /golem/output

# Set the working directory to /app
WORKDIR /golem/work

# Copy the current directory contents into the container at /app
ADD . /golem/work

RUN pip3 install -r /golem/work/requirements.txt

RUN apt-get clean \
    && apt-get -y autoremove

#ENTRYPOINT command and parameters will not be overwritten from command line. 
#Instead, all command line arguments will be added after ENTRYPOINT parameters.
ENTRYPOINT ["python3", "runner.py"]

# CMD sets default command and/or parameters, 
# which can be overwritten from command line when docker container runs.
# CMD ["--do_magic"]
