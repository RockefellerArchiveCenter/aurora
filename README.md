# Aurora

[![Build Status](https://app.travis-ci.com/RockefellerArchiveCenter/aurora.svg?branch=base)](https://app.travis-ci.com/RockefellerArchiveCenter/aurora)
![GitHub (pre-)release](https://img.shields.io/github/release/RockefellerArchiveCenter/aurora/all.svg)

Aurora is a Django web application that can receive, virus check and validate transfers of digital archival records, and allows archivists to appraise and accession those records.

The name of the application is a reference both to the natural light display often seen in the northern hemisphere - sometimes referred to as _aurora borealis_ - as well as the Roman goddess of dawn.

Aurora is part of [Project Electron](http://projectelectron.rockarch.org/), an initiative to build sustainable, open and user-centered infrastructure for the archival management of digital records at the [Rockefeller Archive Center](http://rockarch.org/). Project updates are available on [Bits & Bytes](http://blog.rockarch.org/), the RAC's blog.

## Installation

### Quick Start

If you have [git](https://git-scm.com/) and [Docker](https://www.docker.com/community-edition) installed, getting Aurora up and running is as simple as:
```
git clone https://github.com/RockefellerArchiveCenter/aurora.git
cd aurora
docker-compose up
```
Once the build and startup process has completed, log into Aurora at `http://localhost:8000` with the user/password pair `admin` and `password`.

### Detailed Installation Instructions

1. Install [git](https://git-scm.com/) and [Docker](https://www.docker.com/community-edition)
2. Download or clone this repository
```
$ git clone https://github.com/RockefellerArchiveCenter/aurora.git
```
3. Build and run Aurora. The initial build may take some time, so be patient!
```
$ cd aurora
$ docker-compose up
```

4. Once this process has completed, Aurora is available in your web browser at `http://localhost:8000`. Log in using one of the default user accounts (see "User accounts" below).

#### Installation Notes for Windows Users

By default, when cloning to a Windows machine, git will convert line endings to DOS format, which will cause a variety of issues in the Docker container. To avoid these problems, clone the repo to Windows using `core.autocrlf`
```
$ git clone https://github.com/RockefellerArchiveCenter/aurora.git --config core.autocrlf=input
```

Install the correct version of Docker based on the Windows platform being used. [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/) is available for versions of Windows that do not support [Docker for Windows](https://docs.docker.com/docker-for-windows/).

When using Docker Toolbox, clone aurora to a location in the C:\Users directory. By default, Docker Toolbox only has access to this directory.

Note that with Docker Toolbox, Aurora will not default to run on `http://localhost:8000`. Check the docker ip default:
```
$ docker-machine ip default
```

### Sample Data

If desired, you can import a set of sample bags (not all of which are valid) by running the `import_sample_data.sh` script.

Open up a new terminal window and navigate to the root of the application, then run

```
$ docker-compose exec web import_sample_data
```

### Transferring Your Own Bags

If you'd like to transfer your own bags, note that bags must be serialized as either a TAR (compressed or uncompressed) or ZIP file.

If you'er using S3 storage (see [Transferring digital records](#transferring-digital-records)), you'll need to upload a bag to an S3 bucket configured as an upload bucket for one of your organizations. 

If you're using local storage you can then transfer those bags by SFTPing them into the local container using the credentials below:
- Protocol: `SFTP`
- Host name: `localhost`
- Port number: `22`
- Username: A username associated with an existing user account in Aurora (see below for default accounts)
- Password: The password associated with the user account above

### Data Persistence

The Docker container is currently configured to persist the MySQL database in local storage. This means that when you shut down the container using `docker-compose down` all the data in the application will still be there the next time you run `docker-compose up`. If you want to wipe out the database at shut down, simply run `docker-compose down -v`.


## Authentication

### Disabling OAuth Provider

By default, Aurora is configured to use [Amazon Cognito](https://aws.amazon.com/cognito/)
as an OAuth provider for authentication.

If you don't want to use this method of authentication, it is possible to
use the built-in local Django authentication layer instead. In order to do this
you will need to make a few changes:

1. Update the `MIDDLEWARE` configs in settings.py:
  - Comment out `bag_transfer.middleware.cognito.CognitoAppMiddleware` and
    `bag_transfer.middleware.cognito.CognitoUserMiddleware`.
  - Enable `bag_transfer.middleware.jwt.AuthenticationMiddlewareJWT`.
2. Ensure that the `COGNITO_USE` config value is set to `False`.

### User accounts

By default, Aurora comes with five user accounts:

|Username|Password|User Role|
|---|---|---|
|admin|password|System Administrator|
|donor|password|Read Only User|
|appraiser|password|Appraisal Archivist|
|accessioner|password|Accessioning Archivist|
|manager|password|Managing Archivist|

See the Aurora User Documentation for more information about permissions associated with each user role.

Note that in the Docker container, all user passwords are reset to "password" each time the container is restarted. This behavior can be changed by editing `setup_objects.py`, but note that this change will impact your ability to SFTP bags into the container.

## Transferring digital records

### Transfer Validation

At regularly scheduled intervals, Aurora scans the upload targets for each active
organization. Any new files or directories in the upload target are added to
Aurora's processing queue.

At a high level, transfers are processed as follows:
- Transfers are checked to ensure they have a valid filename, in other words that
  the top-level directory (for unserialized bags) or filename (for serialized bags)
  does not contain illegal characters.
- Transfers are checked for viruses.
- Transfers are checked to ensure they have only one top-level directory.
- Size of transfers is checked to ensure it doesn't exceed `TRANSFER_FILESIZE_MAX`.
- Transfers are validated against the BagIt specification using `bagit-python`.
- Transfers are validated against the BagIt Profile specified in their `bag-info.txt`
  file using `bagit-profiles-validator`.
- Relevant PREMIS rights statements are assigned to transfers (see Organization
  Management section for details).

### Disabling S3 Storage

By default, Aurora is configured to use [Amazon S3](https://aws.amazon.com/s3/) to
store uploaded and validated transfers.

If you don't want to use S3, you can configure Aurora to use the local file system
instead:

1. Set the `S3_USE` config value to `False`.
2. Ensure that the `TRANSFER_UPLOADS_ROOT` is properly set and that the filepath
   specified there exists and is writable by Aurora.s

## API

Aurora comes with a RESTful API, built using the Django Rest Framework. In addition to interacting with the API via your favorite command-line client, you can also use the browsable API interface available in the application.

### Authentication

#### Using OAuth

In order to make requests against the Aurora API when using an OAuth provider, you
will first need to add an application to your OAuth provider, then make a request
against the provider's token endpoint using the client credentials flow. The token
returned from the provider should then be attached as a Bearer token to requests.

The [`ElectronBonder` library](https://github.com/RockefellerArchiveCenter/electronbonder)
contains code which demonstrates this flow (see the `authorize_oauth` method in
`/electronbonder/client.py`).

#### Using local authentication
If OAuth is disabled (see above), Aurora can use JSON Web Tokens for validation. As with all token-based authentication, you should ensure the application is only available over SSL/TLS in order to avoid token tampering and replay attacks.

To get your token, send a POST request to the `/get-token/` endpoint, passing your username and password:

```
$ curl -X POST -d "username=admin&password=password123" http://localhost:8000/api/get-token/
```

Your token will be returned in the response. You can then use the token in requests such as:

```
$ curl -H "Authorization: JWT <your_token>" http://localhost:8000/api/orgs/1/
```

In a production environment, successfully authenticating against this endpoint may require setting Apache's  `WSGIPassAuthorization` to `On`.

The [`ElectronBonder` library](https://github.com/RockefellerArchiveCenter/electronbonder)
contains code which demonstrates this flow (see the `authorize` method in
`/electronbonder/client.py`).


## Django Admin Configuration

Aurora comes with the default [Django admin site](https://docs.djangoproject.com/en/1.11/ref/contrib/admin/). Only users with superuser privileges are able to view this interface, which can be accessed by clicking on the profile menu and selecting "Administration".

In addition to allowing for the manual creation and deletion of certain objects, this interface also allows authorized users to edit system values which are used by the application, including the human-readable strings associated with Bag Log Codes. Care should be taken when making changes in the Django admin interface, particularly the creation or deletion of objects, since they can have unintended consequences.

## Contributing

Aurora is an open source project and we welcome contributions! If you want to fix a bug, or have an idea of how to enhance the application, the process looks like this:

1. File an issue in this repository. This will provide a location to discuss proposed implementations of fixes or enhancements, and can then be tied to a subsequent pull request.
2. If you have an idea of how to fix the bug (or make the improvements), fork the repository and work in your own branch. When you are done, push the branch back to this repository and set up a pull request. Automated unit tests are run on all pull requests. Any new code should have unit test coverage, documentation (if necessary), and should conform to the Python PEP8 style guidelines.
3. After some back and forth between you and core committers (or individuals who have privileges to commit to the base branch of this repository), your code will probably be merged, perhaps with some minor changes.

This repository contains a configuration file for git [pre-commit](https://pre-commit.com/) hooks which help ensure that code is linted before it is checked into version control. It is strongly recommended that you install these hooks locally by installing pre-commit and running `pre-commit install`.


## License

Aurora is released under an [MIT License](LICENSE).
