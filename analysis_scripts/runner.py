from analysis_scripts import geolocator, loc_finder, collector
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# {url: [(city, (lat, long)), ...],...}
def run_and_get_geolocs():
	articles = collector.get_newspaper_articles()

	article_to_loc_map = loc_finder.get_locs(articles)

	geocoder = Nominatim(user_agent='geolocator-news-analyzer')
	geocode = RateLimiter(geocoder.geocode, min_delay_seconds=0.1, return_value_on_exception=None)

	article_to_geoloc_map = {}

	for url in article_to_loc_map.keys():
		gpes = article_to_loc_map[url]
		located_gpes = geolocator.get_locations(gpes, geocode)

		article_to_geoloc_map[url] = located_gpes

	return article_to_geoloc_map





if __name__ == '__main__':
	articles = collector.get_newspaper_articles()[0:5]


	article_to_loc_map = loc_finder.get_locs(articles)

	geocoder = Nominatim(user_agent='geolocator-news-analyzer')
	geocode = RateLimiter(geocoder.geocode, min_delay_seconds=0.1, return_value_on_exception=None)

	article_to_geoloc_map = {}

	for url in article_to_loc_map.keys():
		gpes = article_to_loc_map[url]
		located_gpes = geolocator.get_locations(gpes, geocode)

		article_to_geoloc_map[url] = located_gpes

	print(article_to_geoloc_map)











