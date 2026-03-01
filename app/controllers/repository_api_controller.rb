class RepositoryApiController < ApplicationController
  accept_api_auth :project_repositories

  def project_repositories
    projects = Project.allowed_to(:view_repository, User.current)
                      .includes(:repositories)

    project_data = projects.map do |project|
      {
        id:           project.id,
        name:         project.name,
        repositories: project.repositories.map do |repo|
          {
            id:   repo.id,
            name: repo.name.presence || repo.identifier,
            type: repo.class.name,
            path: repo.url
          }
        end
      }
    end

    render json: { projects: project_data }
  end
end
