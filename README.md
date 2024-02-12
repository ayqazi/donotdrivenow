Do Not Drive Now
================

Should you go out driving now? If a local team is playing, you'll be trapped in traffic. This aims to help you make that decision.

Setup
-----

* Install requirements.txt in your venv
* Set up your local env by copying `.env.local.example` to `.env.local` and editing to your requirements
* Create a venv for Python 3.11 or later
* Install packages from requirements.txt

Run
---

Create DB as configured in `DATABASE_URI` in `.env.local`.

Now commands can be run:

Create DB schema

```shell
VENVPATH/python -m donotdrivenow.bin.initdb
```

Ingest

```shell
VENVPATH/python -m donotdrivenow.bin.football_data
```

The `fixtures` table now contains the gold data that can be used to find out if I should drive now.
