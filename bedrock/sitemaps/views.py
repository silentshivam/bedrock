from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from bedrock.mozorg.decorators import cache_control_expires
from bedrock.sitemaps.models import SitemapURL


@method_decorator(cache_control_expires(1), name='dispatch')
class SitemapView(TemplateView):
    content_type = 'text/xml'

    def _get_locale(self):
        if self.kwargs['is_none']:
            # is_none here refers to the sitemap_none.xml URL. the value of that kwarg
            # when on that URL will be "_none" and will be None if not on that URL.
            # For that page we set the locale to empty string as that is what the entries
            # in the DB have recorded for locale for URLs that don't have a locale.
            locale = ''
        else:
            # can come back as empty string
            # should be None here if not a real locale because
            # None will mean that we should show the index of sitemaps
            # instead of a sitemap for a locale.
            locale = getattr(self.request, 'locale', None) or None

        return locale

    def get_template_names(self):
        if self._get_locale() is None:
            return ['sitemap_index.xml']
        else:
            return ['sitemap.xml']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        locale = self._get_locale()
        if locale is None:
            ctx['locales'] = SitemapURL.objects.all_locales()
        else:
            ctx['paths'] = SitemapURL.objects.all_for_locale(locale)

        return ctx
