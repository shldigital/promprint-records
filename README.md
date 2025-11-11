# Promprint Database
A django-based admin interface for editing and interacting with the [promprint](https://cordis.europa.eu/project/id/101163126) database.

This is currently a work in progress. Only the administration interface for the database is currently available. The front end will be developed as we work out whether the fundamental database structure is what we need.

Promprint will explore rejects of legal deposit in 19th-century UK libraries. The database enables this by storing and comparing separate tables of data:

1) A reference table containing the title, creator and date of all publications listed in the registers of the Stationer's Hall under the copyright act, for a set of dates that is the subject of this research project

2) A table for each of the UK legal deposit libraries, containing all publications (and associated metadata) received by those libraries during the years covered by the registers of the Stationer's Hall

The front end will enable exploration of the data and metadata, allowing us to find gaps in the legal deposit record when referenced to the Stationer's Hall register.

## Installation
The project is managed using [`uv`](https://github.com/astral-sh/uv), and [`docker engine`](https://www.docker.com/).

The data will be published in a portable format so that the whole system can be explored by other researchers. Documentation to follow.

Instructions to install `uv` can be found [here](https://docs.astral.sh/uv/getting-started/installation/).

Instructions to install `docker-engine` can be found [here](https://docs.docker.com/engine/install/)

Once the repo has been cloned, and the database has been copied over (details to follow), the project can be run for development using:

```
uv run python manage.py migrate
uv run python manage.py runserver
```

or it can be run for deployment using:

```
docker compose up --build -d
```

Both will deploy a local server which you can access at `127.0.0.1:8070`

## Tasks
- [X] Create the basic table structure for the Stationer's Hall and Library data, allowing us to start populating that table via both manual and automated transcription of the digitised copies of the registers.
- [X] Explore convenient ways to match data (fuzzy search?) and to build/join new tables that can help research explore themes behind the gaps in the data
- [ ] Once legal deposit data from the British Library is Received, build out the corresponding table based on their metadata structure
- [ ] Convert the project over to use the [django rest framework](https://www.django-rest-framework.org/) to improve interoperability of the front end when it comes

