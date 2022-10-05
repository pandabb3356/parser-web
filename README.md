# parser-web

## Prerequisites
- Python 3.7+
- Redis 4.0+ 
- Postgres 9+
- node 15+

## Setup

### Update Dependencies

#### Python
```bash
$ pyenv virtualenv 3.7.13 parser-web
$ pyenv activate parser-web
$ pip install -r requirements.txt
```
#### Node
```bash
$ nvm install v15
$ nvm use v15
$ npm install
```

### Create Database
```bash
psql -U ${postgres_username} -c "CREATE DATABASE \"parser_web\" ENCODING 'UTF8'
  LC_COLLATE = 'en_US.UTF-8'
  LC_CTYPE = 'en_US.UTF-8';"
```

### Upgrade
```bash
$ pyenv activate parser-web
$ inv db.upgrade
```

### New Migrate File
```bash
$ pyenv activate parser-web
# unmark modify models in web/__init__.py
$ inv db.new_migrate_file
```

### Start Backend Server
```bash
$ inv server
```

### Start Frontend Server
```bash
$ npm run serve
```

### Start Worker (Rq)
```bash
$ inv worker
```

### Third Party
- Microsoft SSO
- Line Bot