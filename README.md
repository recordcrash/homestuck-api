# Homestuck API

A specter is haunting the Homestuck music fan community: the specter of a lack of a good API for Homestuck music. This is a project to fix that.

I'm SICK and TIRED of having to rely on the moldy hsmusic.wiki custom yaml with its custom parser, which doesn't even convert itself to a standard while being parsed... Though an outstanding effort, it unwittingly drives itself into the Microsoft paradigm of Embrace Extend Extinguish. Replaced all the other wikis with a centralized, customized, non-extensible mess

That's why I thought I'd do this. This is a fully fledged API of Homestuck music (for now mostly music, might add more stuff to it later) with standard json fixtures (albums, tracks, references, files, art) that anyone can port to any other engine or database (or just send GET requests to the API to get the data!). The entire API environment can be replicated through everything you can see in this repo.

Massive credits to Niklink for domain knowledge help while setting this up, Nebula for the original music wiki, and every musician and artist involved in Homestuck and Homestuck accessories for their work.

## Local set up

You may need Docker and Docker Compose for this. Running it is easy, though it takes 5GB of disk space. First, create an .env file using the .env.dist template. Then, run these commands to get the Postgres and Django up and running:

```
docker-compose build
docker-compose up
```

That will install the requirements, set up every data model, create a superuser, load the fixtures, etc. It can possibly be run without Docker, but you're on your own for that. You'll need to execute everything in entrypoint.sh manually, set up a postgres instance, and so forth.

There's an additional option if for some reason the jsons are outdated and you want to use the hsmusic.wiki yamls, and that is to get inside the django container and run the following:

```
python manage.py import_hsmusic_yaml
```

This will parse the yaml into Homestuck API models to the best of my ability. Then you can export them to fixtures with the usual `python manage.py dumpdata` command.

The usual warning of never running this in production without disabling the DEBUG variable applies here.

## Online use

HOWEVER, this is an API, so you don't *need* to run it yourself, it will be available at api.homestuck.net. You will need to contact me at Makin#0413 on Discord or makin at protonmail dot com to get edit access to the admin panel, which will allow you to add new albums, new tracks, etc.. it'd be pretty silly if we had to do everything through editing text files manually, right? RIGHT???

The API will be read-only, and I don't plan in enabling instance creation through it. The admin panel should be good enough and also allow me to set up sane dynamic permissions without having to worry about authentication complexity.

## Roadmap

This is a beta release so Niklink and others can check the CRUD django admin behavior. It has no API yet, that's the next step.

The thing is pretty usable, but before we can abandon the yamls, I would like for the following fixes:
- Process commentary so it's split by creator, right now it's all bundled together in one file
- Process artist contribution types correctly, either manually or otherwise
- Add lyrics and sheet music

## License

This project is licensed under the MIT license (this only applies to the code, not the raw data!). See LICENSE for more details.