#! /usr/bin/env python

from airline import app


if __name__ == "__main__":

    app.secret_key = 'laksjlKxalslsaldkkjcakjsh'
    app.run(debug=True)
