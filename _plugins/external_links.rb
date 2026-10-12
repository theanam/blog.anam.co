# Opens links to other sites in a new tab.
#
# Runs on post content after Markdown is converted and before the layout is applied, so only links
# inside posts change; the menu, tag links and pagination are untouched. Links to this blog (site.url,
# plus the old blog.anam.co address that redirects here) and relative links stay in the same tab.
# A link that already sets its own target is left as written.
require "uri"

module ExternalLinks
  OWN_HOSTS = %w[anam.co www.anam.co blog.anam.co].freeze

  def self.external?(href, own_hosts)
    return false unless href.start_with?("http://", "https://", "//")
    host = URI.parse(href.start_with?("//") ? "https:#{href}" : href).host.to_s.downcase
    !own_hosts.include?(host)
  rescue URI::InvalidURIError
    false
  end

  def self.process(html, own_hosts)
    html.gsub(/<a\s[^>]*>/i) do |tag|
      href = tag[/\shref\s*=\s*["']([^"']+)["']/i, 1]
      next tag if href.nil? || tag =~ /\starget\s*=/i || !external?(href, own_hosts)

      # noopener stops the new tab from controlling this page through window.opener.
      if tag =~ /\srel\s*=\s*["']([^"']*)["']/i
        rel = (Regexp.last_match(1).split + ["noopener"]).uniq.join(" ")
        tag = tag.sub(/\srel\s*=\s*["'][^"']*["']/i, %( rel="#{rel}"))
      else
        tag = tag.sub(/>\z/, ' rel="noopener">')
      end
      tag.sub(/>\z/, ' target="_blank">')
    end
  end
end

Jekyll::Hooks.register [:posts], :post_convert do |post|
  own = ExternalLinks::OWN_HOSTS | [URI.parse(post.site.config["url"].to_s).host.to_s.downcase]
  post.content = ExternalLinks.process(post.content, own)
end
