<div align="left">
  <picture>
    <source media="(prefers-color-scheme: dark)"
            srcset="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-dark-transparent-cropped.png" />
    <source media="(prefers-color-scheme: light)"
            srcset="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-light-transparent-cropped.png" />
    <img src="https://github.com/wattnet/.github/raw/main/images/wattnet-logo-full-light-transparent-cropped.png"
         alt="Wattnet Logo"
         width="300" />
  </picture>
</div>

# Python Client

| Category     | Links |
| ------------ | ----- |
| Stack        | [![pandas](https://img.shields.io/badge/pandas-475569?logo=pandas&logoColor=white)](https://pandas.pydata.org/) [![aiohttp](https://img.shields.io/badge/aiohttp-475569?logo=aiohttp&logoColor=white)](https://docs.aiohttp.org/) |
| Repository   | [![Contributors](https://img.shields.io/github/contributors/wattnet/wattnet-client-python?label=Contributors&color=1E293B&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/graphs/contributors) [![Stars](https://img.shields.io/github/stars/wattnet/wattnet-client-python?style=flat&label=Stars&color=1E293B&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/stargazers) |
| Testing & CI | [![CI](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-client-python/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/actions/workflows/ci.yml) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-0F766E?logo=pre-commit&logoColor=white&labelColor=1E293B)](https://github.com/pre-commit/pre-commit) [![Ruff lint](https://img.shields.io/badge/Lint-Ruff-0F766E?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEwIiBoZWlnaHQ9IjYyMiIgdmlld0JveD0iMCAwIDUxMCA2MjIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI%2BPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMDYuNzAxIDBDMjAwLjk2NCAwIDE5Ni4zMTQgNC42NDEzMSAxOTYuMzE0IDEwLjM2NjdWNDEuNDY2N0MxOTYuMzE0IDQ3LjE5MiAxOTEuNjYzIDUxLjgzMzMgMTg1LjkyNyA1MS44MzMzSDE1Ni44NDNDMTUxLjEwNyA1MS44MzMzIDE0Ni40NTYgNTYuNDc0NiAxNDYuNDU2IDYyLjJWMTQ1LjEzM0MxNDYuNDU2IDE1MC44NTkgMTQxLjgwNiAxNTUuNSAxMzYuMDY5IDE1NS41SDEwNi45ODZDMTAxLjI0OSAxNTUuNSA5Ni41OTg4IDE2MC4xNDEgOTYuNTk4OCAxNjUuODY3VjIyMi44ODNDOTYuNTk4OCAyMjguNjA5IDkxLjk0ODQgMjMzLjI1IDg2LjIxMTggMjMzLjI1SDU3LjEyODNDNTEuMzkxNyAyMzMuMjUgNDYuNzQxMyAyMzcuODkxIDQ2Ljc0MTMgMjQzLjYxN1YzMDAuNjMzQzQ2Ljc0MTMgMzA2LjM1OSA0Mi4wOTA5IDMxMSAzNi4zNTQ0IDMxMUgxMC4zODdDNC42NTA0IDMxMSAwIDMxNS42NDEgMCAzMjEuMzY3VjM1Mi40NjdDMCAzNTguMTkyIDQuNjUwNCAzNjIuODMzIDEwLjM4NyAzNjIuODMzSDE0NS40MThDMTUxLjE1NCAzNjIuODMzIDE1NS44MDQgMzY3LjQ3NSAxNTUuODA0IDM3My4yVjQzMC4yMTdDMTU1LjgwNCA0MzUuOTQyIDE1MS4xNTQgNDQwLjU4MyAxNDUuNDE4IDQ0MC41ODNIMTE2LjMzNEMxMTAuNTk3IDQ0MC41ODMgMTA1Ljk0NyA0NDUuMjI1IDEwNS45NDcgNDUwLjk1VjUwNy45NjdDMTA1Ljk0NyA1MTMuNjkyIDEwMS4yOTcgNTE4LjMzMyA5NS41NjAxIDUxOC4zMzNINjYuNDc2NkM2MC43NCA1MTguMzMzIDU2LjA4OTYgNTIyLjk3NSA1Ni4wODk2IDUyOC43VjYxMS42MzNDNTYuMDg5NiA2MTcuMzU5IDYwLjc0IDYyMiA2Ni40NzY2IDYyMkgxNDkuNTcyQzE1NS4zMDkgNjIyIDE1OS45NTkgNjE3LjM1OSAxNTkuOTU5IDYxMS42MzNWNTcwLjE2N0gyMDEuNTA3QzIwNy4yNDQgNTcwLjE2NyAyMTEuODk0IDU2NS41MjUgMjExLjg5NCA1NTkuOFY1MjguN0MyMTEuODk0IDUyMi45NzUgMjE2LjU0NCA1MTguMzMzIDIyMi4yODEgNTE4LjMzM0gyNTEuMzY1QzI1Ny4xMDEgNTE4LjMzMyAyNjEuNzUyIDUxMy42OTIgMjYxLjc1MiA1MDcuOTY3VjQ3Ni44NjdDMjYxLjc1MiA0NzEuMTQxIDI2Ni40MDIgNDY2LjUgMjcyLjEzOCA0NjYuNUgzMDEuMjIyQzMwNi45NTkgNDY2LjUgMzExLjYwOSA0NjEuODU5IDMxMS42MDkgNDU2LjEzM1Y0MjUuMDMzQzMxMS42MDkgNDE5LjMwOCAzMTYuMjU5IDQxNC42NjcgMzIxLjk5NiA0MTQuNjY3SDM1MS4wNzlDMzU2LjgxNiA0MTQuNjY3IDM2MS40NjYgNDEwLjAyNSAzNjEuNDY2IDQwNC4zVjM3My4yQzM2MS40NjYgMzY3LjQ3NSAzNjYuMTE3IDM2Mi44MzMgMzcxLjg1MyAzNjIuODMzSDQwMC45MzdDNDA2LjY3MyAzNjIuODMzIDQxMS4zMjQgMzU4LjE5MiA0MTEuMzI0IDM1Mi40NjdWMzIxLjM2N0M0MTEuMzI0IDMxNS42NDEgNDE1Ljk3NCAzMTEgNDIxLjcxMSAzMTFINDUwLjc5NEM0NTYuNTMxIDMxMSA0NjEuMTgxIDMwNi4zNTkgNDYxLjE4MSAzMDAuNjMzVjIxNy43QzQ2MS4xODEgMjExLjk3NSA0NTYuNTMxIDIwNy4zMzMgNDUwLjc5NCAyMDcuMzMzSDQyMC42NzJDNDE0LjkzNiAyMDcuMzMzIDQxMC4yODUgMjAyLjY5MiA0MTAuMjg1IDE5Ni45NjdWMTY1Ljg2N0M0MTAuMjg1IDE2MC4xNDEgNDE0LjkzNiAxNTUuNSA0MjAuNjcyIDE1NS41SDQ0OS43NTZDNDU1LjQ5MiAxNTUuNSA0NjAuMTQzIDE1MC44NTkgNDYwLjE0MyAxNDUuMTMzVjExNC4wMzNDNDYwLjE0MyAxMDguMzA4IDQ2NC43OTMgMTAzLjY2NyA0NzAuNTMgMTAzLjY2N0g0OTkuNjEzQzUwNS4zNSAxMDMuNjY3IDUxMCA5OS4wMjUzIDUxMCA5My4zVjEwLjM2NjdDNTEwIDQuNjQxMzIgNTA1LjM1IDAgNDk5LjYxMyAwSDIwNi43MDFaTTE2OC4yNjkgNDQwLjU4M0MxNjIuNTMyIDQ0MC41ODMgMTU3Ljg4MiA0NDUuMjI1IDE1Ny44ODIgNDUwLjk1VjUwNy45NjdDMTU3Ljg4MiA1MTMuNjkyIDE1My4yMzEgNTE4LjMzMyAxNDcuNDk1IDUxOC4zMzNIMTE4LjQxMUMxMTIuNjc1IDUxOC4zMzMgMTA4LjAyNCA1MjIuOTc1IDEwOC4wMjQgNTI4LjdWNTU5LjhDMTA4LjAyNCA1NjUuNTI1IDExMi42NzUgNTcwLjE2NyAxMTguNDExIDU3MC4xNjdIMTU5Ljk1OVY1MjguN0MxNTkuOTU5IDUyMi45NzUgMTY0LjYxIDUxOC4zMzMgMTcwLjM0NiA1MTguMzMzSDE5OS40M0MyMDUuMTY2IDUxOC4zMzMgMjA5LjgxNyA1MTMuNjkyIDIwOS44MTcgNTA3Ljk2N1Y0NzYuODY3QzIwOS44MTcgNDcxLjE0MSAyMTQuNDY3IDQ2Ni41IDIyMC4yMDQgNDY2LjVIMjQ5LjI4N0MyNTUuMDI0IDQ2Ni41IDI1OS42NzQgNDYxLjg1OSAyNTkuNjc0IDQ1Ni4xMzNWNDI1LjAzM0MyNTkuNjc0IDQxOS4zMDggMjY0LjMyNSA0MTQuNjY3IDI3MC4wNjEgNDE0LjY2N0gyOTkuMTQ1QzMwNC44ODEgNDE0LjY2NyAzMDkuNTMyIDQxMC4wMjUgMzA5LjUzMiA0MDQuM1YzNzMuMkMzMDkuNTMyIDM2Ny40NzUgMzE0LjE4MiAzNjIuODMzIDMxOS45MTkgMzYyLjgzM0gzNDkuMDAyQzM1NC43MzkgMzYyLjgzMyAzNTkuMzg5IDM1OC4xOTIgMzU5LjM4OSAzNTIuNDY3VjMyMS4zNjdDMzU5LjM4OSAzMTUuNjQxIDM2NC4wMzkgMzExIDM2OS43NzYgMzExSDM5OC44NTlDNDA0LjU5NiAzMTEgNDA5LjI0NiAzMDYuMzU5IDQwOS4yNDYgMzAwLjYzM1YyNjkuNTMzQzQwOS4yNDYgMjYzLjgwOCA0MDQuNTk2IDI1OS4xNjcgMzk4Ljg1OSAyNTkuMTY3SDMxOC44OEMzMTMuMTQzIDI1OS4xNjcgMzA4LjQ5MyAyNTQuNTI1IDMwOC40OTMgMjQ4LjhWMjE3LjdDMzA4LjQ5MyAyMTEuOTc1IDMxMy4xNDMgMjA3LjMzMyAzMTguODggMjA3LjMzM0gzNDcuOTYzQzM1My43IDIwNy4zMzMgMzU4LjM1IDIwMi42OTIgMzU4LjM1IDE5Ni45NjdWMTY1Ljg2N0MzNTguMzUgMTYwLjE0MSAzNjMuMDAxIDE1NS41IDM2OC43MzcgMTU1LjVIMzk3LjgyMUM0MDMuNTU3IDE1NS41IDQwOC4yMDggMTUwLjg1OSA0MDguMjA4IDE0NS4xMzNWMTE0LjAzM0M0MDguMjA4IDEwOC4zMDggNDEyLjg1OCAxMDMuNjY3IDQxOC41OTUgMTAzLjY2N0g0NDcuNjc4QzQ1My40MTUgMTAzLjY2NyA0NTguMDY1IDk5LjAyNTMgNDU4LjA2NSA5My4zVjYyLjJDNDU4LjA2NSA1Ni40NzQ2IDQ1My40MTUgNTEuODMzMyA0NDcuNjc4IDUxLjgzMzNIMjA4Ljc3OEMyMDMuMDQxIDUxLjgzMzMgMTk4LjM5MSA1Ni40NzQ2IDE5OC4zOTEgNjIuMlYxNDUuMTMzQzE5OC4zOTEgMTUwLjg1OSAxOTMuNzQxIDE1NS41IDE4OC4wMDQgMTU1LjVIMTU4LjkyMUMxNTMuMTg0IDE1NS41IDE0OC41MzQgMTYwLjE0MSAxNDguNTM0IDE2NS44NjdWMjIyLjg4M0MxNDguNTM0IDIyOC42MDkgMTQzLjg4MyAyMzMuMjUgMTM4LjE0NyAyMzMuMjVIMTA5LjA2M0MxMDMuMzI3IDIzMy4yNSA5OC42NzYyIDIzNy44OTEgOTguNjc2MiAyNDMuNjE3VjMwMC42MzNDOTguNjc2MiAzMDYuMzU5IDEwMy4zMjcgMzExIDEwOS4wNjMgMzExSDE5Ny4zNTJDMjAzLjA4OSAzMTEgMjA3LjczOSAzMTUuNjQxIDIwNy43MzkgMzIxLjM2N1Y0MzAuMjE3QzIwNy43MzkgNDM1Ljk0MiAyMDMuMDg5IDQ0MC41ODMgMTk3LjM1MiA0NDAuNTgzSDE2OC4yNjlaIiBmaWxsPSIjZmZmZmZmIi8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://docs.astral.sh/ruff/linter/) |
| Release      | [![Release](https://img.shields.io/github/v/release/wattnet/wattnet-client-python?label=Release&color=3B5B8A&logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/releases) [![Publish](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-client-python/publish.yml?label=Publish&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/actions/workflows/publish.yml) [![Release Please](https://img.shields.io/github/actions/workflow/status/wattnet/wattnet-client-python/release-please.yml?branch=main&label=Release%20Please&logo=githubactions&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/actions/workflows/release-please.yml) |
| Package      | [![PyPI](https://img.shields.io/pypi/v/wattnet-client?label=PyPI&color=9C5A32&logo=pypi&logoColor=white&labelColor=1E293B)](https://pypi.org/project/wattnet-client/) [![Python](https://img.shields.io/pypi/pyversions/wattnet-client?label=Python&color=9C5A32&logo=python&logoColor=white&labelColor=1E293B)](https://pypi.org/project/wattnet-client/) [![Downloads](https://img.shields.io/pepy/dt/wattnet-client?label=Downloads&color=9C5A32&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZiI%2BPHBhdGggZD0iTTExIDNoMnY5LjE3bDMuNTktMy41OEwxOCAxMGwtNiA2LTYtNiAxLjQxLTEuNDFMMTEgMTIuMTdWM3oiLz48cGF0aCBkPSJNNCAxOWgxNnYySDR6Ii8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://pepy.tech/projects/wattnet-client) |
| Quality      | [![Status](https://img.shields.io/badge/Status-Beta-4A8118?labelColor=1E293B)](https://pypi.org/project/wattnet-client/) [![Coverage](https://img.shields.io/codecov/c/github/wattnet/wattnet-client-python?label=Coverage&logo=codecov&logoColor=white&labelColor=1E293B)](https://codecov.io/gh/wattnet/wattnet-client-python) [![Ruff format](https://img.shields.io/badge/Format-Ruff-4A8118?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTEwIiBoZWlnaHQ9IjYyMiIgdmlld0JveD0iMCAwIDUxMCA2MjIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI%2BPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMDYuNzAxIDBDMjAwLjk2NCAwIDE5Ni4zMTQgNC42NDEzMSAxOTYuMzE0IDEwLjM2NjdWNDEuNDY2N0MxOTYuMzE0IDQ3LjE5MiAxOTEuNjYzIDUxLjgzMzMgMTg1LjkyNyA1MS44MzMzSDE1Ni44NDNDMTUxLjEwNyA1MS44MzMzIDE0Ni40NTYgNTYuNDc0NiAxNDYuNDU2IDYyLjJWMTQ1LjEzM0MxNDYuNDU2IDE1MC44NTkgMTQxLjgwNiAxNTUuNSAxMzYuMDY5IDE1NS41SDEwNi45ODZDMTAxLjI0OSAxNTUuNSA5Ni41OTg4IDE2MC4xNDEgOTYuNTk4OCAxNjUuODY3VjIyMi44ODNDOTYuNTk4OCAyMjguNjA5IDkxLjk0ODQgMjMzLjI1IDg2LjIxMTggMjMzLjI1SDU3LjEyODNDNTEuMzkxNyAyMzMuMjUgNDYuNzQxMyAyMzcuODkxIDQ2Ljc0MTMgMjQzLjYxN1YzMDAuNjMzQzQ2Ljc0MTMgMzA2LjM1OSA0Mi4wOTA5IDMxMSAzNi4zNTQ0IDMxMUgxMC4zODdDNC42NTA0IDMxMSAwIDMxNS42NDEgMCAzMjEuMzY3VjM1Mi40NjdDMCAzNTguMTkyIDQuNjUwNCAzNjIuODMzIDEwLjM4NyAzNjIuODMzSDE0NS40MThDMTUxLjE1NCAzNjIuODMzIDE1NS44MDQgMzY3LjQ3NSAxNTUuODA0IDM3My4yVjQzMC4yMTdDMTU1LjgwNCA0MzUuOTQyIDE1MS4xNTQgNDQwLjU4MyAxNDUuNDE4IDQ0MC41ODNIMTE2LjMzNEMxMTAuNTk3IDQ0MC41ODMgMTA1Ljk0NyA0NDUuMjI1IDEwNS45NDcgNDUwLjk1VjUwNy45NjdDMTA1Ljk0NyA1MTMuNjkyIDEwMS4yOTcgNTE4LjMzMyA5NS41NjAxIDUxOC4zMzNINjYuNDc2NkM2MC43NCA1MTguMzMzIDU2LjA4OTYgNTIyLjk3NSA1Ni4wODk2IDUyOC43VjYxMS42MzNDNTYuMDg5NiA2MTcuMzU5IDYwLjc0IDYyMiA2Ni40NzY2IDYyMkgxNDkuNTcyQzE1NS4zMDkgNjIyIDE1OS45NTkgNjE3LjM1OSAxNTkuOTU5IDYxMS42MzNWNTcwLjE2N0gyMDEuNTA3QzIwNy4yNDQgNTcwLjE2NyAyMTEuODk0IDU2NS41MjUgMjExLjg5NCA1NTkuOFY1MjguN0MyMTEuODk0IDUyMi45NzUgMjE2LjU0NCA1MTguMzMzIDIyMi4yODEgNTE4LjMzM0gyNTEuMzY1QzI1Ny4xMDEgNTE4LjMzMyAyNjEuNzUyIDUxMy42OTIgMjYxLjc1MiA1MDcuOTY3VjQ3Ni44NjdDMjYxLjc1MiA0NzEuMTQxIDI2Ni40MDIgNDY2LjUgMjcyLjEzOCA0NjYuNUgzMDEuMjIyQzMwNi45NTkgNDY2LjUgMzExLjYwOSA0NjEuODU5IDMxMS42MDkgNDU2LjEzM1Y0MjUuMDMzQzMxMS42MDkgNDE5LjMwOCAzMTYuMjU5IDQxNC42NjcgMzIxLjk5NiA0MTQuNjY3SDM1MS4wNzlDMzU2LjgxNiA0MTQuNjY3IDM2MS40NjYgNDEwLjAyNSAzNjEuNDY2IDQwNC4zVjM3My4yQzM2MS40NjYgMzY3LjQ3NSAzNjYuMTE3IDM2Mi44MzMgMzcxLjg1MyAzNjIuODMzSDQwMC45MzdDNDA2LjY3MyAzNjIuODMzIDQxMS4zMjQgMzU4LjE5MiA0MTEuMzI0IDM1Mi40NjdWMzIxLjM2N0M0MTEuMzI0IDMxNS42NDEgNDE1Ljk3NCAzMTEgNDIxLjcxMSAzMTFINDUwLjc5NEM0NTYuNTMxIDMxMSA0NjEuMTgxIDMwNi4zNTkgNDYxLjE4MSAzMDAuNjMzVjIxNy43QzQ2MS4xODEgMjExLjk3NSA0NTYuNTMxIDIwNy4zMzMgNDUwLjc5NCAyMDcuMzMzSDQyMC42NzJDNDE0LjkzNiAyMDcuMzMzIDQxMC4yODUgMjAyLjY5MiA0MTAuMjg1IDE5Ni45NjdWMTY1Ljg2N0M0MTAuMjg1IDE2MC4xNDEgNDE0LjkzNiAxNTUuNSA0MjAuNjcyIDE1NS41SDQ0OS43NTZDNDU1LjQ5MiAxNTUuNSA0NjAuMTQzIDE1MC44NTkgNDYwLjE0MyAxNDUuMTMzVjExNC4wMzNDNDYwLjE0MyAxMDguMzA4IDQ2NC43OTMgMTAzLjY2NyA0NzAuNTMgMTAzLjY2N0g0OTkuNjEzQzUwNS4zNSAxMDMuNjY3IDUxMCA5OS4wMjUzIDUxMCA5My4zVjEwLjM2NjdDNTEwIDQuNjQxMzIgNTA1LjM1IDAgNDk5LjYxMyAwSDIwNi43MDFaTTE2OC4yNjkgNDQwLjU4M0MxNjIuNTMyIDQ0MC41ODMgMTU3Ljg4MiA0NDUuMjI1IDE1Ny44ODIgNDUwLjk1VjUwNy45NjdDMTU3Ljg4MiA1MTMuNjkyIDE1My4yMzEgNTE4LjMzMyAxNDcuNDk1IDUxOC4zMzNIMTE4LjQxMUMxMTIuNjc1IDUxOC4zMzMgMTA4LjAyNCA1MjIuOTc1IDEwOC4wMjQgNTI4LjdWNTU5LjhDMTA4LjAyNCA1NjUuNTI1IDExMi42NzUgNTcwLjE2NyAxMTguNDExIDU3MC4xNjdIMTU5Ljk1OVY1MjguN0MxNTkuOTU5IDUyMi45NzUgMTY0LjYxIDUxOC4zMzMgMTcwLjM0NiA1MTguMzMzSDE5OS40M0MyMDUuMTY2IDUxOC4zMzMgMjA5LjgxNyA1MTMuNjkyIDIwOS44MTcgNTA3Ljk2N1Y0NzYuODY3QzIwOS44MTcgNDcxLjE0MSAyMTQuNDY3IDQ2Ni41IDIyMC4yMDQgNDY2LjVIMjQ5LjI4N0MyNTUuMDI0IDQ2Ni41IDI1OS42NzQgNDYxLjg1OSAyNTkuNjc0IDQ1Ni4xMzNWNDI1LjAzM0MyNTkuNjc0IDQxOS4zMDggMjY0LjMyNSA0MTQuNjY3IDI3MC4wNjEgNDE0LjY2N0gyOTkuMTQ1QzMwNC44ODEgNDE0LjY2NyAzMDkuNTMyIDQxMC4wMjUgMzA5LjUzMiA0MDQuM1YzNzMuMkMzMDkuNTMyIDM2Ny40NzUgMzE0LjE4MiAzNjIuODMzIDMxOS45MTkgMzYyLjgzM0gzNDkuMDAyQzM1NC43MzkgMzYyLjgzMyAzNTkuMzg5IDM1OC4xOTIgMzU5LjM4OSAzNTIuNDY3VjMyMS4zNjdDMzU5LjM4OSAzMTUuNjQxIDM2NC4wMzkgMzExIDM2OS43NzYgMzExSDM5OC44NTlDNDA0LjU5NiAzMTEgNDA5LjI0NiAzMDYuMzU5IDQwOS4yNDYgMzAwLjYzM1YyNjkuNTMzQzQwOS4yNDYgMjYzLjgwOCA0MDQuNTk2IDI1OS4xNjcgMzk4Ljg1OSAyNTkuMTY3SDMxOC44OEMzMTMuMTQzIDI1OS4xNjcgMzA4LjQ5MyAyNTQuNTI1IDMwOC40OTMgMjQ4LjhWMjE3LjdDMzA4LjQ5MyAyMTEuOTc1IDMxMy4xNDMgMjA3LjMzMyAzMTguODggMjA3LjMzM0gzNDcuOTYzQzM1My43IDIwNy4zMzMgMzU4LjM1IDIwMi42OTIgMzU4LjM1IDE5Ni45NjdWMTY1Ljg2N0MzNTguMzUgMTYwLjE0MSAzNjMuMDAxIDE1NS41IDM2OC43MzcgMTU1LjVIMzk3LjgyMUM0MDMuNTU3IDE1NS41IDQwOC4yMDggMTUwLjg1OSA0MDguMjA4IDE0NS4xMzNWMTE0LjAzM0M0MDguMjA4IDEwOC4zMDggNDEyLjg1OCAxMDMuNjY3IDQxOC41OTUgMTAzLjY2N0g0NDcuNjc4QzQ1My40MTUgMTAzLjY2NyA0NTguMDY1IDk5LjAyNTMgNDU4LjA2NSA5My4zVjYyLjJDNDU4LjA2NSA1Ni40NzQ2IDQ1My40MTUgNTEuODMzMyA0NDcuNjc4IDUxLjgzMzNIMjA4Ljc3OEMyMDMuMDQxIDUxLjgzMzMgMTk4LjM5MSA1Ni40NzQ2IDE5OC4zOTEgNjIuMlYxNDUuMTMzQzE5OC4zOTEgMTUwLjg1OSAxOTMuNzQxIDE1NS41IDE4OC4wMDQgMTU1LjVIMTU4LjkyMUMxNTMuMTg0IDE1NS41IDE0OC41MzQgMTYwLjE0MSAxNDguNTM0IDE2NS44NjdWMjIyLjg4M0MxNDguNTM0IDIyOC42MDkgMTQzLjg4MyAyMzMuMjUgMTM4LjE0NyAyMzMuMjVIMTA5LjA2M0MxMDMuMzI3IDIzMy4yNSA5OC42NzYyIDIzNy44OTEgOTguNjc2MiAyNDMuNjE3VjMwMC42MzNDOTguNjc2MiAzMDYuMzU5IDEwMy4zMjcgMzExIDEwOS4wNjMgMzExSDE5Ny4zNTJDMjAzLjA4OSAzMTEgMjA3LjczOSAzMTUuNjQxIDIwNy43MzkgMzIxLjM2N1Y0MzAuMjE3QzIwNy43MzkgNDM1Ljk0MiAyMDMuMDg5IDQ0MC41ODMgMTk3LjM1MiA0NDAuNTgzSDE2OC4yNjlaIiBmaWxsPSIjZmZmZmZmIi8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://docs.astral.sh/ruff/formatter/) |
| Community    | [![Contributing](https://img.shields.io/badge/Contributing-guidelines-5374A7?logo=github&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/blob/main/CONTRIBUTING.md) [![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-3.0-5374A7?logo=contributorcovenant&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/blob/main/CODE_OF_CONDUCT.md) [![Security](https://img.shields.io/badge/Security-policy-5374A7?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2ZmZiI%2BPHBhdGggZD0iTTcgMTBWN2E1IDUgMCAwIDEgMTAgMHYzaDFhMiAyIDAgMCAxIDIgMnY4YTIgMiAwIDAgMS0yIDJINmEyIDIgMCAwIDEtMi0ydi04YTIgMiAwIDAgMSAyLTJoMXptMiAwaDZWN2EzIDMgMCAxIDAtNiAwdjN6Ii8%2BPC9zdmc%2B&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/blob/main/SECURITY.md) [![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-5374A7?logo=conventionalcommits&logoColor=white&labelColor=1E293B)](https://www.conventionalcommits.org/) |
| License      | [![Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-64748B?logo=opensourceinitiative&logoColor=white&labelColor=1E293B)](https://github.com/wattnet/wattnet-client-python/blob/main/LICENSE) |

`wattnet-client` is the official Python client for the [wattnet API](https://github.com/wattnet/wattnet-api). It maps every API endpoint to a client method and hands back a [pandas](https://pandas.pydata.org/) `DataFrame` — no manual HTTP calls or JSON flattening required.

## Features

- **One method per endpoint** — `client.get_generation(...)`, `client.get_footprints(...)`, etc., mirroring the API 1:1.
- **DataFrames by default** — every method returns a tidy `pandas.DataFrame`. Need the raw JSON instead? Use `WattnetRawClient`.
- **Sync and async** — `WattnetClient` and `WattnetRawClient` for scripts and notebooks, `AsyncWattnetClient` and `AsyncWattnetRawClient` for asyncio applications.
- **Two ways to authenticate** — a static bearer token, or the `client_id` and `client_secret` of a wattnet credential; the library fetches and caches tokens for you.
- **Typed, autocomplete-friendly** — zone codes, production types, footprint scopes, etc. are typed for IDE/Jupyter tab-completion.

See [`examples/quickstart.ipynb`](examples/quickstart.ipynb) for every method exercised against the real API, with actual DataFrame outputs saved in the notebook.

## Installation

```bash
pip install wattnet-client
```

### From source

```bash
git clone https://github.com/wattnet/wattnet-client-python.git
cd wattnet-client-python
poetry install
```

## Quickstart

```python
from wattnet.client import WattnetClient

# Option 1: a pre-issued bearer token
client = WattnetClient(token="<your-token>")

# Option 2: a wattnet credential — the client fetches and caches a token for you
client = WattnetClient(client_id="<your-client-id>", client_secret="<your-client-secret>")

# Every call returns a pandas DataFrame
df = client.get_generation(zone="ES", production_type="solar")
df = client.get_footprints(zone="ES", footprint_type="carbon", scope="life-cycle")
df = client.get_environmental_score(zone="ES", aggregate=True, start="2026-01-01", end="2026-02-01")
```

Filter by coordinates instead of a zone code:

```python
df = client.get_load(lat=40.4, lon=-3.7)
```

Every time-series `DataFrame` has a `timestamp` column parsed as a tz-aware
(UTC) `datetime64[ns, UTC]`, ready to plot or resample without any manual
conversion. Omit `zone` (and other filter params) to get every zone back in
a single call instead of querying one at a time.

### Authentication

A credential (`client_id` and `client_secret`) is created in the [developer portal](https://developer.wattnet.eu). The client exchanges it for a bearer token with the OAuth 2.0 `client_credentials` grant the first time it's needed, keeps the token in memory, and renews it once 80 % of its lifetime has passed (but never later than a minute before it expires). If the API still rejects the cached token as expired, the client refreshes it and retries the request once.

```python
client = WattnetClient(client_id="<your-client-id>", client_secret="<your-client-secret>")
```

Read the secret from an environment variable or a secrets manager rather than writing it in code. The token endpoint is discovered from the OpenID Connect issuer (`https://auth.wattnet.eu/realms/wattnet`).

### Raw JSON access

If you need the untouched API response instead of a DataFrame, use `WattnetRawClient` — it exposes the exact same methods:

```python
from wattnet.client import WattnetRawClient

raw = WattnetRawClient(token="<your-token>")
payload = raw.get_generation(zone="ES")  # list[dict], straight from the API
```

### Async client

For asyncio applications (for example the [wattnet Home Assistant integration](https://github.com/wattnet/wattnet-home-assistant)) use `AsyncWattnetRawClient`. It exposes the same methods as `WattnetRawClient`, every one of them a coroutine, and returns raw JSON. It is built on [aiohttp](https://docs.aiohttp.org/) and does not import pandas. If you prefer DataFrames, `AsyncWattnetClient` is its counterpart of `WattnetClient`: the same methods as coroutines returning a `pandas.DataFrame`.

```python
import asyncio

from wattnet.client import AsyncWattnetRawClient


async def main() -> None:
    async with AsyncWattnetRawClient(token="<your-token>") as client:
        zones = await client.get_zones()
        footprints = await client.get_footprints(zone="ES", footprint_type="carbon")


asyncio.run(main())
```

```python
from wattnet.client import AsyncWattnetClient

async with AsyncWattnetClient(token="<your-token>") as client:
    df = await client.get_footprints(zone="ES", footprint_type="carbon")
```

Pass your own `aiohttp.ClientSession` with `session=...` to reuse an existing connection pool. A session you supply is never closed by the client. Authentication, retries, `Retry-After` handling and the token refresh on a 401 behave exactly as in the synchronous clients. 

## Available methods

| Method                                                        | API endpoint          | Description                                                  |
| --------------------------------------------------------------- | ---------------------- | ------------------------------------------------------------- |
| `get_zones()`                                                    | `GET /zones`            | Metadata and neighbours for all supported zones               |
| `get_generation(...)`                                            | `GET /generation`       | Electricity generation by production type                     |
| `get_load(...)`                                                  | `GET /load`             | Total electricity demand                                      |
| `get_imports(...)`                                               | `GET /imports`          | Electricity imports, optionally filtered by origin zone        |
| `get_exports(...)`                                               | `GET /exports`          | Electricity exports, optionally filtered by destination zone   |
| `get_mix(...)`                                                   | `GET /mix`              | Flow-traced generation mix by production type                 |
| `get_footprints(...)`                                            | `GET /footprints`       | Carbon/water footprint of consumption                         |
| `get_impacts(...)`                                               | `GET /impacts`          | Water impact of consumption                                    |
| `get_environmental_score(...)`                                           | `GET /environmental-score`      | EnvironmentalScore (0–100) of consumption                              |
| `get_flow_share(...)`                                            | `GET /flow-share`       | Share of a zone's production exported to each destination      |
| `get_mix_share(...)`                                             | `GET /mix-share`        | Share of a zone's mix coming from each origin                  |
| `get_footprint_share(...)`                                       | `GET /footprint-share`  | Footprint decomposed by origin zone                            |
| `get_impact_share(...)`                                          | `GET /impact-share`     | Impact decomposed by origin zone                               |
| `get_factors(...)`                                               | `GET /factors`          | Global emission/consumption factors                            |
| `get_status()` / `get_status_storage()` / `get_status_entsoe()` / `get_status_elexon()` / `get_status_epias()` | `GET /status[/...]` | Health of the API and its upstream dependencies |

Every method's parameters mirror the corresponding API endpoint's query parameters exactly — see each method's docstring/type hints, or the [wattnet-api docs](https://api.wattnet.eu/docs) for the full parameter reference.

`get_zones()` and `get_factors(...)` are cached in memory per client instance for an hour (they're near-static reference data) — repeated calls within that window don't hit the network again.

## Configuration

| Constructor argument | Environment variable      | Default                                 |
| --------------------- | -------------------------- | ---------------------------------------- |
| `base_url`            | `WATTNET_API_BASE_URL`     | `https://api.wattnet.eu/v1`               |
| `issuer_url`          | `WATTNET_ISSUER_URL`       | `https://auth.wattnet.eu/realms/wattnet`  |
| `token_url`           | `WATTNET_TOKEN_URL`        | read from the issuer's discovery document |

Other constructor options: `session` (bring your own `requests.Session`), `timeout`, `retry_count`, `retry_delay`.

Requests are retried up to `retry_count` times (default 3, waiting `retry_delay` seconds between attempts) on connection/timeout errors and on `429`/`5xx` responses — a `429` waits for the `Retry-After` value the API sends instead of the fixed delay, when present. A `401` always triggers one token refresh + retry, independent of `retry_count`.

`WattnetClient`/`WattnetRawClient` support the context manager protocol, closing
the underlying HTTP session on exit:

```python
with WattnetClient(token="<your-token>") as client:
    df = client.get_zones()
```

`repr(client)` shows the base URL and auth mode (e.g. `WattnetClient(base_url='https://api.wattnet.eu/v1', auth=StaticTokenProvider)`) — never any credentials.

## Error handling

All errors raised by this library derive from `wattnet.client.WattnetError`:

- `ConfigurationError` — the client was instantiated with invalid/incomplete auth arguments.
- `AuthenticationError` — invalid token or credentials.
- `WattnetAPIError` — the API returned a non-2xx response; carries `.status_code` and `.detail`.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, code style, and how to run the tests.

## License

This repository is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

See the [LICENSE](LICENSE) file for more details.

## Funding and Acknowledgments

This work was developed within the [GreenDIGIT](https://greendigit-project.eu/) project, funded by the European Union's Horizon Europe research and innovation programme under grant agreement No. [101131207](https://cordis.europa.eu/project/id/101131207), and by the Swiss State Secretariat for Education, Research and Innovation (SERI).

<img src="https://github.com/wattnet/.github/raw/main/images/GreenDIGIT logo color horizontal2.png" alt="GreenDIGIT Logo" width="230" align="right"/>
<img src="https://github.com/wattnet/.github/raw/main/images/EN_FundedbytheEU_RGB_POS.png" alt="EU Funded Logo" width="260" align="left"/>
<img src="https://github.com/wattnet/.github/raw/main/images/Flag_of_Switzerland.svg" alt="Swiss State Secretariat for Education, Research and Innovation (SERI)" height="50" align="left"/>
<br clear="all"/>

##### © 2026 Spanish National Research Council (CSIC). All rights reserved.

