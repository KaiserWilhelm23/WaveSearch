# WaveSearch

Version: 0.0.0 (NOT OFFICALLY RELEASED YET)

License: GNU General Public License v3.0

Project Lead: William Payne

## Overview

WaveSearch is a high-speed dataset search engine designed for radio and communications enthusiasts. It unifies access to multiple FCC and FAA datasets, enabling rapid lookups without relying on third-party APIs or restrictive services. WaveSearch replaces aging tools like HamDB, offering cleaner data, offline capabilities, and community-driven development.

## Supported Datasets

WaveSearch currently provides instant search across:

* Amateur Radio (HAM): FCC ULS call signs, FRNs, and license data

* GMRS: General Mobile Radio Service records for family and business use

* Tower Structures: FCC Antenna Structure Registration (ASR) listings (Still improper parsing)

* Aviation: FAA and FCC registered communications infrastructure data

All datasets are moslty parsed, filtered, and indexed in JSON format for fast local querying.

## Features

* Instant lookup across multiple dataset types

* Lightweight, offline-capable JSON format

* Works locally or on a LAN-hosted server

* Community-driven and fully open source

* Flexible filtering on fields such as call sign, FRN, city, state, and more


## Installing locally 


Python is required!!!!! This install follows the linux command line not CMD on Windows, However it does work on Windows 11.

Clone or download the repository:
```
git clone https://github.com/KaiserWilhelm23/WaveSearch.git
cd WaveSearch
```

Run one of the download scripts in the dscpts/ directory to fetch your desired dataset(s). You can choose a single dataset or all of them.
```
ls dscpts
python3 dscpts/[download_script].py 
```

Start the server!!!! 
```
python3 server.py
```


## Contribution

WaveSearch is fully open source under the GNU license. Contributions are welcome:

* Fix bugs or improve filtering algorithms

* Add new datasets or enhance dataset parsing

* Improve UI/UX or accessibility

Please submit pull requests via the official repository.
