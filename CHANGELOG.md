# Changelog

## [1.0.0](https://github.com/wattnet/wattnet-client-python/compare/v1.0.0...v1.0.0) (2026-11-26)


### Features

* add async client with async auth, raw client and DataFrame support ([3f9b640](https://github.com/wattnet/wattnet-client-python/commit/3f9b6403644ae24f40fcbaccd3aaf21c5b15bb71))
* add Python 3.15 support ([7984045](https://github.com/wattnet/wattnet-client-python/commit/79840456b3d5f40d3f9f067e5296d045eed53970))
* add Python 3.15 support ([dce9219](https://github.com/wattnet/wattnet-client-python/commit/dce92198ceb518c8813ddcb1c460f991c8148bb1))
* authenticate with client_id and client_secret instead of email and password ([8f538d7](https://github.com/wattnet/wattnet-client-python/commit/8f538d7264790e16a48adc0eb40b3ca25fc1e2b9))
* authenticate with client_id and client_secret instead of email and password ([3877431](https://github.com/wattnet/wattnet-client-python/commit/3877431bc97e9e57fbb1f6346001910dcc4948e8))
* enhance API client with zone type safety and improved documentation ([ac9d17f](https://github.com/wattnet/wattnet-client-python/commit/ac9d17ffb42277bd44e6cf2790da1930030a3798))
* expand zone codes in enums for improved type safety and autocomplete ([c669636](https://github.com/wattnet/wattnet-client-python/commit/c669636d39788fc6e1debd69d2cfd727e7c0e32e))
* order the columns of every DataFrame the same way ([#33](https://github.com/wattnet/wattnet-client-python/issues/33)) ([6eb7455](https://github.com/wattnet/wattnet-client-python/commit/6eb74553b7cef1fe17e47f489c439c781595bf86))
* read points and updated_at, add resolution, compression and error codes ([#28](https://github.com/wattnet/wattnet-client-python/issues/28)) ([4ecfd4b](https://github.com/wattnet/wattnet-client-python/commit/4ecfd4b827ec48fbee35132e05c9de76226d604a))


### Bug Fixes

* require pandas 3 on Python 3.15 and accept any datetime64 unit in tests ([ba69d3b](https://github.com/wattnet/wattnet-client-python/commit/ba69d3bee5e12728d6bd4c9ebfbc8f3bc1d93dd3))


### Documentation

* add async clients to quickstart notebook and link Home Assistant integration ([eed6715](https://github.com/wattnet/wattnet-client-python/commit/eed67151694c09f3769b81dbdc41042e26a00eba))
* add quickstart notebook with live API outputs ([bbaa5f9](https://github.com/wattnet/wattnet-client-python/commit/bbaa5f97f4d0f8977d6a315a25b883a69e5ae8ee))
* add README, licence and community health files ([3f955a4](https://github.com/wattnet/wattnet-client-python/commit/3f955a4ad3761584216694b08bf571b7743d44de))
* add stars, downloads and isort badges to README ([818d93d](https://github.com/wattnet/wattnet-client-python/commit/818d93d6ff04d48a34ff75d8a34c53aab14f32dd))
* add stars, downloads and isort badges to README ([f9ac1b1](https://github.com/wattnet/wattnet-client-python/commit/f9ac1b1132cd540569d783602f407588f19d6f93))
* align community files with the repository reference ([49fc1a2](https://github.com/wattnet/wattnet-client-python/commit/49fc1a23bfb1dd4c8596f74b15696633c61427c9))
* fix the address of the developer portal ([#29](https://github.com/wattnet/wattnet-client-python/issues/29)) ([e0de61d](https://github.com/wattnet/wattnet-client-python/commit/e0de61dc370a48bd9d062574d363633512e63b55))
* link the published Python client documentation ([878d797](https://github.com/wattnet/wattnet-client-python/commit/878d79769a739f02223ac60a8c2dd28642a85479))
* refresh the README badge table ([fa81219](https://github.com/wattnet/wattnet-client-python/commit/fa8121921bf4d41a193790cb7ee02b0d17ce14eb))


### Build System

* **deps:** bump aiohttp from 3.14.4 to 3.14.5 ([018f6db](https://github.com/wattnet/wattnet-client-python/commit/018f6dbb5d1c35d863c13b36e376757e65f1380a))
* **deps:** bump aiohttp from 3.14.4 to 3.14.5 ([691ba93](https://github.com/wattnet/wattnet-client-python/commit/691ba93b86c1d7745160d3ae4d46ff9d10fe1f4b))
* **deps:** bump mistune from 3.3.3 to 3.3.4 ([#32](https://github.com/wattnet/wattnet-client-python/issues/32)) ([c9eecf7](https://github.com/wattnet/wattnet-client-python/commit/c9eecf77a177b364eae0b1d39b1b197fddb81c86))
* **deps:** bump nbconvert ([a968ba3](https://github.com/wattnet/wattnet-client-python/commit/a968ba3b71c417d5c44ad74c0badafb4ed86c11c))
* **deps:** bump nbconvert from 7.17.1 to 7.17.2 in the dev-dependencies group ([3d566ee](https://github.com/wattnet/wattnet-client-python/commit/3d566ee0c6af8677f18f876f3ec8d50ccdc184ed))
* **deps:** bump the dev-dependencies group across 1 directory with 5 updates ([33289f4](https://github.com/wattnet/wattnet-client-python/commit/33289f4e867c9b3d1972b63b3176148e15f47106))
* **deps:** bump the dev-dependencies group across 1 directory with 5 updates ([7bbcaa6](https://github.com/wattnet/wattnet-client-python/commit/7bbcaa62f01a575a1a9e16d5765bc5f181cc606b))
* **deps:** bump the dev-dependencies group across 1 directory with 5 updates ([12a2a5f](https://github.com/wattnet/wattnet-client-python/commit/12a2a5fb554a19085b052a9aaa8e3bbe6ea53263))
* **deps:** bump the dev-dependencies group across 1 directory with 9 updates ([d1ce42a](https://github.com/wattnet/wattnet-client-python/commit/d1ce42affb789b14342b4e58a305b61e6745ccd4))
* **deps:** bump the dev-dependencies group with 3 updates ([#31](https://github.com/wattnet/wattnet-client-python/issues/31)) ([4ee91ec](https://github.com/wattnet/wattnet-client-python/commit/4ee91ecdabeb5cdd950ea4cc32d06b0dd17dd7b9))
* **deps:** bump the dev-dependencies group with 5 updates ([#27](https://github.com/wattnet/wattnet-client-python/issues/27)) ([4f66b35](https://github.com/wattnet/wattnet-client-python/commit/4f66b35b66fc16cd08e6093f9ec762394ef8a96a))
* **deps:** bump the dev-dependencies group with 6 updates ([b34957f](https://github.com/wattnet/wattnet-client-python/commit/b34957f11a16371f3060fb2655501d858fef4d1b))
* **deps:** bump the dev-dependencies group with 6 updates ([0d4e62b](https://github.com/wattnet/wattnet-client-python/commit/0d4e62bd1e5ab57e9527039a41cfd312cb43ae02))
* drop support for Python 3.10 and update the vulnerable dependencies in the lock ([#26](https://github.com/wattnet/wattnet-client-python/issues/26)) ([28c8186](https://github.com/wattnet/wattnet-client-python/commit/28c818688c1eac4a0e2b1828778036413de93a34))
* exempt tests and examples from docstring and line length rules ([1f3ec97](https://github.com/wattnet/wattnet-client-python/commit/1f3ec971d2ff2b317438f0314f4751db513209e4))
* migrate to Ruff and refresh README badges ([4e7b014](https://github.com/wattnet/wattnet-client-python/commit/4e7b014d76dcb68e181be6f3b6843aef9588cc1e))
* replace flake8, black, and isort with Ruff ([b24084e](https://github.com/wattnet/wattnet-client-python/commit/b24084e77a7a485980ae354c061559b5e4033934))
