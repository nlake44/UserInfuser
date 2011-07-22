require 'net/http'
require 'uri'

module TestHelper
  def self.post(path, params)
    uri = URI.parse(path)
    response = Net::HTTP.post_form(uri, params)
    return response.body
  end
end

