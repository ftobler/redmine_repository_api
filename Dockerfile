ARG REDMINE_VERSION=6.1
FROM redmine:${REDMINE_VERSION}

# this just demonstrates how to add custom gems in the docker-compose infrastructure.

RUN \
    # echo "gem 'jwt'" >> Gemfile && \
    gosu redmine bundle install && \
    # fix permissions for running as an arbitrary user
	chmod -R ugo=rwX Gemfile.lock "$GEM_HOME" && \
	rm -rf ~redmine/.bundle
