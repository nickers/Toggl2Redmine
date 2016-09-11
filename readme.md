Toggl2Redmine
===

`Toggl2Redmine` is an app for one way synchronizing **[toggl](toggl.com)** entries to **[redmine](https://www.redmine.org/)** time entries associated with **issues**. All toggl entries decorated with issue id (see example) will be treated as entries to send to redmine time entries.

Optionally after synchronization this app sends a notification to *mattermost*.

Example
---

I record a time entry and give it a comment: `Tracing bug for #345`. Running a `synchronizer` will insert a redmine time entry with comment `Tracing bug for #345 [toggl#0000]` at issue #345 (`[toggl#0000]` is a time entry decorator added by `synchronizer` to track unique toggl time entry id).

Issue id must start with hash sign (*#*) and can be placed anywhere in comment.

Requirements
---

* Toggl account and api key
* Redmine URL
* Redmine account and api key
* [Optional] Mattermost incoming webhook url

How to run
---

If you don't have *python 3* installed, go to **Releases** and download executable. It is the simplest way to run `toggl2redmine`.

If you have *python 3* installed you should prepare once a new virtual environment and download requirements (see Howto). Then always when you want to run *synchronizer* you should firstly activate environment:

```
.env\Scripts\activate.bat
python -m toggltoredmine.synchronizer
```

Usage
---

Get help:

```
synchronizer -h
```

Run synchronizer for last day:

```
synchronizer -d 1
```

Run synchronizer for last day in simulation mode:

```
synchronizer -d 1 -s
```

Howto
---

**Prepare development environemnt**

```
python -m venv .env
.env\Scripts\activate.bat (or .sh)
pip install -r requirements.txt
```

**Run tests**

```
nosetests -v
```

**Run tests with coverage**

```
nosetests --with-coverage --cover-html
```

**Prepare executable**

```
pyinstaller synchronizer.spec
```
