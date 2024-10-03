# metadata-gathering

A Python API that returns metadata for text files in JSON format, allows CSV download, and is containerized in Docker with automated file download, along with example unit testing and usage instructions.

## Prerequisites 

* This project is developed and tested on macOS.

* You will need the `brew` macOS package management tool in order to install various prerequisites.

* You will need **python3.10** installed on your machine.

* This project uses [direnv](https://direnv.net/) for automatic context management. First run `brew install direnv`. "direnv" allows you to automatically run commands whenever you `cd` into the project's root dir. It runs the [.envrc](.envrc) file. The project root will be automatically added to the environment variable PYTHONPATH.

* You will also need [poetry](https://python-poetry.org/). "poetry" is a python environment management tool that makes it incredibly easy to resolve dependencies and install them. Poetry allows you to "lock" package versions at a given time and install the same versions consistently as long as the ".lock" file is untouched. The "[poetry.lock](poetry.lock)" file has already been created and checked in this repo for your convenience, and the `poetry install` command will run automatically through "direnv", along with poetry's environment activation command.

## Quick Setup

1. clone this repo with `git clone &&&`    # &&& also test here.
2. run `cd metadata-gathering`
3. run `make env_create`
4. run `make docker_build`
5. run `make docker_run`
6. in another terminal, cd into project root again with `cd metadata-gathering`
7. run `make client_run`

For detailed explanations, jump to **Makefile** section.

## Modules

The project is divided into 2 modules in separate python project packages: 

* [app.py](server/app.py), which contains the "business logic". This module implements a Flask application that has two API routes. After any of the 2 routes is hit by an API request, this module will download the zip file, extract it locally, build the metadata, and based on the route hit, it will send the data back to the client either as CSV or as JSON. 

The server app is also dockerized, i.e. a docker image is build and a container is run, which will include the Flask app and expose it on port 4000. See [Dockerfile](Dockerfile) for more info.

* [client.py](client/client.py), which imitates a potential client/user. It's simple code that makes 2 HTTP requests to the app server and pulls the metadata using both CSV and JSON.

To run the client, run `python client/client.py` from the project root, or simply run `make client_run`.

## Tests

I've included 6 tests, 3 test cases for the app's `download_and_extract_zip` function, and 3 for the `generate_metadata` func. In practice, I could have added tests only for the `generate_metadata`, since its execution includes the execution of `download_and_extract_zip`, but I just wanted to have tests for at least 2 different functions. I could have expended the test framework by adding a bunch of different tests for corner cases, and add tests for every single function, but in the interest of time, I've added these 6 tests only to show a sound unit testing framework.

## Makefile

For your convenience, there is a Makefile that includes all the commands you will need to build, run, and test the app.

* `make env_create` - If you are setting up this project for the first time, run this in order to create a new poetry environment, resolve dependencies and install them.

* `make env_update` - Run this in order to re-resolve dependencies and install them. You would use this if you haven't resolved dependencies in a long time and newer versions of dependencies are available, but not currently installed.

* `make env_install` - syncs the dependencies with the .lock file, created by the targets above.

* `make test` - run the test suite.

* `docker_reqs` - called by the `docker_build` target and there is no point in calling it separately. It creates a requirement.txt file based on the poetry environment we already set up. It's used in the container.

* `make docker_build` - build the docker image.

* `make docker_run` - run a new container based on the docker image created above. At this point the Flask application is ready to take in requests.

* `make client_run` - this will trigger 2 HTTP requests to the containerized application, display JSON on stdout and place `interview.csv` file in project root.

## Considerations and divergement from the project reqs

* The [project requirements](https://gist.github.com/BrainMonkey/538bce394963eef23f862b33d885dcce) state that the Docker container should be named following the pattern `wmt-<firstname>-<lastname>-file-metadata:0.0.1`, which seems to include image tag. Probably what the reqs mean is that the **image** should be named that way instead. I've assumed that, so I named the container itself after the image, subtract the tag and add `-container`, which in my particular case ends up being `wmt-martin-klosi-file-metadata-container`. For more info, see lines 2-6 in [Makefile](Makefile).

* It's not 100% clear from the reqs whether we need to dockerize the server app, client app or both. Further down in the reqs it's mentioned that running the dockerized application should put the result (interview.csv) into the local directory, without mention of making any API requests. I assumed here that the reqs actually meant to dockerize the server app. This is what I would do in a real-world scenario. After dockerizing the server app, I would deploy it behind a load balancer, in a distributed and auto-scalable way, through Kubernetes or AWS ECS.

* Finally, I'm submitting this project as a Github repo, even though the reqs state it should be a zip/tgz file. I think it's cleaner this way and mimics a real world scenario. Also, it says on the email from my recruiter, Sarvani Velivela, that I could submit as a GH repo, if I chose to do so. quote: "Once you are done, please send the deliverables back to the recruiter, a GitHub repo is also acceptable."

## Future/Potential Improvements

* Introduce user authentication. This means that I would need 2 additional routes. 
1. `/create-user` - this will take in username and password as request params, store them in a db and return an authentication token, which the user can use in every other subsequent request. Without this token, the `/get-metadata-csv` and `/get-metadata-json` routes will return code 403.
2. `/login-user` - this will take in username and password as request params, check whether such user exists and whether hashed password matches and return auth token. 

* Make the routes only accept HTTPS requests with authentication and certification.

* Use multiprocessing in the server application when a request is handled to process each of the files independently.
