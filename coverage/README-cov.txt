To run a new coverage test over the application, run:

python -m pytest --cov=. test >> coverage/coverage.txt

over the main directory of the repository ImHere/

As of 12/10/16, we are at 84% code coverage.
Most of the missing 16% can be accounted for in our main executable that initially runs the application
and an authentication script that deals with the Google Single Sign-On functionality.