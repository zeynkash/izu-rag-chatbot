import scrapy


class IzuScraperItem(scrapy.Item):
    """
    Main item structure for scraped university data
    """
    # Basic Information
    url = scrapy.Field()
    title = scrapy.Field()
    language = scrapy.Field()
    
    # Content
    content = scrapy.Field()
    meta_description = scrapy.Field()
    breadcrumb = scrapy.Field()
    
    # Categorization
    section = scrapy.Field()
    subsection = scrapy.Field()
    
    # Media & Documents
    images = scrapy.Field()
    documents = scrapy.Field()
    
    # Additional Info
    contact_info = scrapy.Field()
    last_updated = scrapy.Field()
    date_scraped = scrapy.Field()
    
    # Technical
    response_status = scrapy.Field()
    content_length = scrapy.Field()
