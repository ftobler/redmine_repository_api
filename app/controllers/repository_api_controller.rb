class RepositoryApiController < ApplicationController
  before_action :require_login
  accept_api_auth :project_repositories

  def project_repositories
    projects = Project.allowed_to(:view_repository, User.current)
                      .includes(:repositories)

    project_data = projects.map do |project|
      repos = project.repositories

      if params[:type].present?
        repos = repos.select { |r| r.class.name.split('::').last.casecmp?(params[:type]) }
      end

      {
        id:           project.id,
        name:         project.name,
        repositories: repos.map do |repo|
          {
            id:   repo.id,
            name: repo.name.presence || repo.identifier,
            type: repo.class.name,
            path: repo.url
          }
        end
      }
    end

    if params[:non_empty].present? && params[:non_empty] != '0' && params[:non_empty] != 'false'
      project_data = project_data.select { |p| p[:repositories].any? }
    end

    render json: { projects: project_data }
  end
end
