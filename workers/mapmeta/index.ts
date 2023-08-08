import { ExecutionContext, R2Bucket } from '@cloudflare/workers-types'

interface Env {
  BUCKET: R2Bucket
  CACHE_MAX_AGE?: number
  ALLOWED_ORIGINS?: string
}

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    if (request.method !== 'GET') {
      return new Response(`Unsupported method`, {
        status: 400,
      })
    }

    let allowedOrigin = ''
    if (typeof env.ALLOWED_ORIGINS !== 'undefined') {
      for (const o of env.ALLOWED_ORIGINS.split(',')) {
        if (o === request.headers.get('Origin') || o === '*') {
          allowedOrigin = o
        }
      }
    }

    const url = new URL(request.url)
    const objectName = decodeURI(url.pathname.slice(1))

    const cacheKey = new Request(url.toString(), request)
    const cache = caches.default

    let response = await cache.match(cacheKey)

    if (response) {
      // cache hit, return response wih access control headers
      const responseHeaders = new Headers(response.headers)
      if (allowedOrigin)
        responseHeaders.set('Access-Control-Allow-Origin', allowedOrigin)
      responseHeaders.set('Vary', 'Origin')

      return new Response(response.body, {
        headers: responseHeaders,
        status: response.status,
      })
    } else {
      // cache miss, fetch from bucket
      const object = await env.BUCKET.get(objectName)

      if (object === null) {
        return new Response('Not Found', { status: 404 })
      }

      const headers = new Headers()
      object.writeHttpMetadata(headers)
      headers.set('etag', object.httpEtag)

      if (allowedOrigin)
        headers.set('Access-Control-Allow-Origin', allowedOrigin)
      headers.set('Vary', 'Origin')
      headers.set('Cache-Control', 'max-age=' + (env.CACHE_MAX_AGE || 86400))

      response = new Response(object.body, {
        headers,
        status: 200,
      })

      ctx.waitUntil(cache.put(cacheKey, response.clone()))
    }

    return response
  },
}
