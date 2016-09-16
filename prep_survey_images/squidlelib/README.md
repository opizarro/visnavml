# squidlelib #

Library for interacting with SQUIDLE+ API.

### Setup ###

```
#!bash

git clone git@bitbucket.org:ariell/squidlelib.git
cd squidlelib/
pip install -r requirements.txt
```

Checkout "examples". Run examples from root directory (so modules can be found). For example:

```
#!python

python examples/run_remote_annotation_algorithm.py <str:api_token> <int:annotation_set_id>
```

Where ```<str:api_token>``` is the API TOKEN of the user that will be making requests from the API, and ```<int:annotation_set_id>``` is the annotation_set_id than can be found in the URL of a selected annotation set.