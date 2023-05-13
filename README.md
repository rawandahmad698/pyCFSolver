<h3>
        <h3>CapSolver.com</h3>
        <br>
        <a href="https://dashboard.capsolver.com/passport/register?inviteCode=G2QOL-c1l_7z">
            <img src="https://cdn.discordapp.com/attachments/1105172394655625306/1105180101802471575/20221207-160749.gif" alt="Capsolver's Banner">
        </a>
</h3>
<br>
At the lowest price on the market, you may receive a variety of solutions, including reCAPTCHA V2, reCAPTCHA V3, hCaptcha, hCaptcha Click, FunCaptcha, picture-to-text, and more. With this service, 0.1s is the slowest speed ever measured.
<hr>

# pyCFSolver

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

pyCFSolver is a fork of (FlareSolver) which is a proxy server to bypass Cloudflare and DDoS-GUARD protection.

### Features
- [x] All V3 FlareSolverr features
- [x] Proxy Support
- [x] Session support (Ty @furdarius & @Xefir)

### TODO
- [ ] Add Docker support


## How it works

pyCFSolver starts a proxy server, and it waits for user requests in an idle state using few resources.
When some request arrives, it uses [Selenium](https://www.selenium.dev) with the
[undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
to create a web browser (Chrome). It opens the URL with user parameters and waits until the Cloudflare challenge
is solved (or timeout). The HTML code and the cookies are sent back to the user, and those cookies can be used to
bypass Cloudflare using other HTTP clients.

**NOTE**: Web browsers consume a lot of memory. If you are running pyCFSolver on a machine with few RAM, do not make
many requests at once. With each request a new browser is launched.

It is also possible to use a permanent session. However, if you use sessions, you should make sure to close them as
soon as you are done using them.

## Installation

### Docker

Not supported yet. See manual installation.

### Precompiled binaries

Precompiled binaries are not currently available for v3. Please see https://github.com/FlareSolverr/FlareSolverr/issues/660 for updates,
or below for instructions of how to build pyCFSolver from source code.

### From source code

* Install [Python 3.10](https://www.python.org/downloads/).
* Install [Chrome](https://www.google.com/intl/en_us/chrome/) or [Chromium](https://www.chromium.org/getting-involved/download-chromium/) web browser.
* (Only in Linux / macOS) Install [Xvfb](https://en.wikipedia.org/wiki/Xvfb) package.
* Clone this repository and open a shell in that path.
* Run `pip install -r requirements.txt` command to install pyCFSolver dependencies.
* Run `python src/flaresolverr.py` command to start pyCFSolver.

### Systemd service

We provide an example Systemd unit file `flaresolverr.service` as reference. You have to modify the file to suit your needs: paths, user and environment variables.

## Usage

Example request:
```bash
curl -L -X POST 'http://localhost:8192/v1' \
-H 'Content-Type: application/json' \
--data-raw '{
  "cmd": "request.get",
  "url":"http://www.google.com/",
  "maxTimeout": 60000, 
  "proxy": {"url": "http://0.0.0.0:8888"}
}'
```

Create a session:
```bash
curl -L -X POST 'http://localhost:8192/v1' \
-H 'Content-Type: application/json' \
--data-raw '{
  "cmd": "sessions.create",
  "session": "session_id_1",
  "headless": true,
}'
```
Use a session:
```bash
curl -L -X POST 'http://localhost:8192/v1' \
-H 'Content-Type: application/json' \
--data-raw '{
  "cmd": "request.get",
  "url":"http://www.google.com/",
  "maxTimeout": 60000, 
  "session": "session_id_1",
  "session_ttl_minutes": 10, # Time to live in minutes
  "proxy": {"url": "http://0.0.0.0:8888"}
}'
```

Destroy a session:
```bash
curl -L -X POST 'http://localhost:8192/v1' \
-H 'Content-Type: application/json' \
--data-raw '{
  "cmd": "sessions.destroy",
  "session": "session_id_1",
}'
```


### Commands

#### + `sessions.create`

This will launch a new browser instance which will retain cookies until you destroy it with `sessions.destroy`.
This comes in handy, so you don't have to keep solving challenges over and over and you won't need to keep sending
cookies for the browser to use.

This also speeds up the requests since it won't have to launch a new browser instance for every request.

| Parameter | Notes                                                                                                                                                                                                                 |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| session   | Optional. The session ID that you want to be assigned to the instance. If isn't set a random UUID will be assigned.                                                                                                   |
| proxy     | Optional, default disabled. Eg: `"proxy": {"url": "http://127.0.0.1:8888"}`. You must include the proxy schema in the URL: `http://`, `socks4://` or `socks5://`. Authorization (username/password) is not supported. |

#### + `sessions.list`

Returns a list of all the active sessions. More for debugging if you are curious to see how many sessions are running.
You should always make sure to properly close each session when you are done using them as too many may slow your
computer down.

Example response:

```json
{
  "sessions": [
    "session_id_1",
    "session_id_2",
    "session_id_3..."
  ]
}
```

#### + `sessions.destroy`

This will properly shut down a browser instance and remove all files associated with it to free up resources for a new
session. When you no longer need to use a session you should make sure to close it.

| Parameter | Notes                                         |
|-----------|-----------------------------------------------|
| session   | The session ID that you want to be destroyed. |

#### + `request.get`

| Parameter         | Notes                                                                                                                                                                                                                                                                                                                                        |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| url               | Mandatory                                                                                                                                                                                                                                                                                                                                    |
| session           | Optional. Will send the request from and existing browser instance. If one is not sent it will create a temporary instance that will be destroyed immediately after the request is completed.                                                                                                                                                |
| maxTimeout        | Optional, default value 60000. Max timeout to solve the challenge in milliseconds.                                                                                                                                                                                                                                                           |
| cookies           | Optional. Will be used by the headless browser. Follow [this](https://github.com/puppeteer/puppeteer/blob/v3.3.0/docs/api.md#pagesetcookiecookies) format.                                                                                                                                                                                   |
| returnOnlyCookies | Optional, default false. Only returns the cookies. Response data, headers and other parts of the response are removed.                                                                                                                                                                                                                       |
| proxy             | Optional, default disabled. Eg: `"proxy": {"url": "http://127.0.0.1:8888"}`. You must include the proxy schema in the URL: `http://`, `socks4://` or `socks5://`. Authorization (username/password) is not supported. (When the `session` parameter is set, the proxy is ignored; a session specific proxy can be set in `sessions.create`.) |

:warning: If you want to use Cloudflare clearance cookie in your scripts, make sure you use the pyCFSolver User-Agent too. If they don't match you will see the challenge.

Example response from running the `curl` above:

```json
{
    "solution": {
        "url": "https://www.google.com/?gws_rd=ssl",
        "status": 200,
        "headers": {
            "status": "200",
            "date": "Thu, 16 Jul 2020 04:15:49 GMT",
            "expires": "-1",
            "cache-control": "private, max-age=0",
            "content-type": "text/html; charset=UTF-8",
            "strict-transport-security": "max-age=31536000",
            "p3p": "CP=\"This is not a P3P policy! See g.co/p3phelp for more info.\"",
            "content-encoding": "br",
            "server": "gws",
            "content-length": "61587",
            "x-xss-protection": "0",
            "x-frame-options": "SAMEORIGIN",
            "set-cookie": "1P_JAR=2020-07-16-04; expires=Sat..."
        },
        "response":"<!DOCTYPE html>...",
        "cookies": [
            {
                "name": "NID",
                "value": "204=QE3Ocq15XalczqjuDy52HeseG3zAZuJzID3R57...",
                "domain": ".google.com",
                "path": "/",
                "expires": 1610684149.307722,
                "size": 178,
                "httpOnly": true,
                "secure": true,
                "session": false,
                "sameSite": "None"
            },
            {
                "name": "1P_JAR",
                "value": "2020-07-16-04",
                "domain": ".google.com",
                "path": "/",
                "expires": 1597464949.307626,
                "size": 19,
                "httpOnly": false,
                "secure": true,
                "session": false,
                "sameSite": "None"
            }
        ],
        "userAgent": "Windows NT 10.0; Win64; x64) AppleWebKit/5..."
    },
    "status": "ok",
    "message": "",
    "startTimestamp": 1594872947467,
    "endTimestamp": 1594872949617,
    "version": "1.0.0"
}
```

### + `request.post`

This is the same as `request.get` but it takes one more param:

| Parameter | Notes                                                                    |
|-----------|--------------------------------------------------------------------------|
| postData  | Must be a string with `application/x-www-form-urlencoded`. Eg: `a=b&c=d` |

## Environment variables

| Name            | Default                | Notes                                                                                                                                                         |
|-----------------|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LOG_LEVEL       | info                   | Verbosity of the logging. Use `LOG_LEVEL=debug` for more information.                                                                                         |
| LOG_HTML        | false                  | Only for debugging. If `true` all HTML that passes through the proxy will be logged to the console in `debug` level.                                          |
| CAPTCHA_SOLVER  | none                   | Captcha solving method. It is used when a captcha is encountered. See the Captcha Solvers section.                                                            |
| TZ              | UTC                    | Timezone used in the logs and the web browser. Example: `TZ=Europe/London`.                                                                                   |
| HEADLESS        | true                   | Only for debugging. To run the web browser in headless mode or visible.                                                                                       |
| BROWSER_TIMEOUT | 40000                  | If you are experiencing errors/timeouts because your system is slow, you can try to increase this value. Remember to increase the `maxTimeout` parameter too. |
| TEST_URL        | https://www.google.com | pyCFSolver makes a request on start to make sure the web browser is working. You can change that URL if it is blocked in your country.                      |
| PORT            | 8191                   | Listening port. You don't need to change this if you are running on Docker.                                                                                   |
| HOST            | 0.0.0.0                | Listening interface. You don't need to change this if you are running on Docker.                                                                              |

Environment variables are set differently depending on the operating system. Some examples:
* Docker: Take a look at the Docker section in this document. Environment variables can be set in the `docker-compose.yml` file or in the Docker CLI command.
* Linux: Run `export LOG_LEVEL=debug` and then start pyCFSolver in the same shell.
* Windows: Open `cmd.exe`, run `set LOG_LEVEL=debug` and then start pyCFSolver in the same shell.

## Captcha Solvers

:warning: At this time none of the captcha solvers work. You can check the status in the open issues. Any help is welcome.

Sometimes CloudFlare not only gives mathematical computations and browser tests, sometimes they also require the user to
solve a captcha.
If this is the case, pyCFSolver will return the error `Captcha detected but no automatic solver is configured.`

pyCFSolver can be customized to solve the captcha automatically by setting the environment variable `CAPTCHA_SOLVER`
to the file name of one of the adapters inside the [/captcha](src/captcha) directory.

## Related projects

* C# implementation => https://github.com/FlareSolverr/FlareSolverrSharp
