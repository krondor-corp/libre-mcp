.PHONY: install serve build clean

install: ## Install gems
	@bundle install

serve: ## Serve the wiki locally with livereload
	@bundle exec jekyll serve --livereload

build: ## Build the static site into _site
	@bundle exec jekyll build

clean: ## Remove the built site
	@rm -rf _site .jekyll-cache
