# marthas-dashboard

Project currently modeled off these resources:

1. [Flask project structure documentation](http://flask.pocoo.org/docs/0.12/patterns/packages/)
2. [Bokeh-flask sample project](https://github.com/bokeh/bokeh/tree/master/examples/embed/simple)

## Setup

Create/activate virtual environment (optional)
```bash
mkdir venvs
cd venvs
python3 -m venv marthas_dashboard
source marthas_dashboard/bin/activate
```

Install flask app (Inside the cloned repo) (NOT optional)
```
# install packages
pip install bokeh flask

# editable install of marthas_dashboard
pip install -e .
```

## To Run

```bash
# export environment variable
export FLASK_APP=marthas_dashboard
export FLASK_DEBUG=true

# Launch it
flask run
```

**Note**: Here is more info on `pip install -e `, which does an [editable install](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs).
