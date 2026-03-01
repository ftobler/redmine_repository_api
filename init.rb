

Redmine::Plugin.register :redmine_repository_api do
  name 'Redmine Repository API'
  author 'Florin Tobler'
  author_url 'https://github.com/ftobler'
  description 'Exposes a REST API endpoint listing projects and their repositories.'
  url 'https://github.com/ftobler/redmine_repository_api'
  version '0.0.1'
  requires_redmine :version_or_higher => '6.1.0'
end
