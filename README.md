# AppSignal Python

AppSignal solves all your Python monitoring needs in a single tool. You and
your team can focus on writing code and we'll provide the alerts if your app
has any issues.

- [AppSignal.com website][appsignal]
- [Documentation][python docs]
- [Support][contact]

[![PyPI - Version](https://img.shields.io/pypi/v/appsignal.svg)](https://pypi.org/project/appsignal)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/appsignal.svg)](https://pypi.org/project/appsignal)

## Description

The AppSignal package collects exceptions and performance data from your Ruby
applications and sends it to AppSignal for analysis. Get alerted when an error
occurs or an endpoint is responding very slowly.

## Usage

First make sure you've installed AppSignal in your application by following the
steps in [Installation](#installation).

AppSignal will automatically monitor requests, report any exceptions that are
thrown and any performance issues that might have occurred.

You can also add extra information by adding custom instrumentation and by tags.

## Installation

Please follow our [installation guide] in our documentation. We try to
automatically instrument as many packages as possible, but may not always be
able to. Make to sure follow any [instructions to add manual
instrumentation][manual instrumentation].

[installation guide]: https://docs.appsignal.com/python/installation
[manual instrumentation]: https://docs.appsignal.com/python/instrumentations

## Development

AppSignal for Python uses [Hatch](https://hatch.pypa.io/latest/) to manage
dependencies, packaging and development environments.

```sh
pip install hatch
```

### Publishing

Publishing is done using [mono](https://github.com/appsignal/mono/). Install it
before development on the project.

```sh
mono publish
```

### Linting and type checking

```sh
hatch run lint:all

hatch run lint:fmt # auto-formatting only
hatch run lint:style # style checking only
hatch run lint:typing # type checking only
```

### Running tests

```sh
hatch run test:pytest
```

### Running the CLI command

```sh
hatch shell
appsignal
```

### Building wheels

```sh
hatch run build:all # for all platforms
hatch run build:me # for your current platform
hatch run build:for <triple> # for a specific agent triple
```

#### Custom agent build
```sh
hatch run build:me /path/to/agent
# or place the desired agent binary at
# `src/appsignal/appsignal-agent`, and then:
hatch run build:me --keep-agent
```

### Clean up build artifacts
```sh
hatch clean # clean dist folder
rm -r tmp # clean agent build cache
```

## Contributing

Thinking of contributing to our package? Awesome! 🚀

Please follow our [Contributing guide][contributing-guide] in our
documentation and follow our [Code of Conduct][coc].

Also, we would be very happy to send you Stroopwafles. Have look at everyone
we send a package to so far on our [Stroopwafles page][waffles-page].

## Support

[Contact us][contact] and speak directly with the engineers working on
AppSignal. They will help you get set up, tweak your code and make sure you get
the most out of using AppSignal.

Also see our [SUPPORT.md file](SUPPORT.md).

[appsignal]: https://www.appsignal.com
[appsignal-sign-up]: https://appsignal.com/users/sign_up
[contact]: mailto:support@appsignal.com
[python docs]: https://docs.appsignal.com/python
[semver]: http://semver.org/
[waffles-page]: https://www.appsignal.com/waffles
[coc]: https://docs.appsignal.com/appsignal/code-of-conduct.html
[contributing-guide]: https://docs.appsignal.com/appsignal/contributing.html
