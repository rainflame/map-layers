import { R2Bucket } from '@cloudflare/workers-types'

interface Env {
  BUCKET: R2Bucket
}

function objectNotFound(objectName: string): Response {
  return new Response(
    `<html><body>R2 object "<b>${objectName}</b>" not found</body></html>`,
    {
      status: 404,
      headers: {
        'content-type': 'text/html; charset=UTF-8',
      },
    },
  )
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)
    const objectName = decodeURI(url.pathname.slice(1))

    console.log(`${request.method} object ${objectName}: ${request.url}`)

    if (request.method === 'GET') {
      const object = await env.BUCKET.get(objectName)

      if (object === null) {
        return new Response('Object Not Found', { status: 404 })
      }

      const headers = new Headers()
      object.writeHttpMetadata(headers)
      headers.set('etag', object.httpEtag)

      return new Response(object.body, {
        headers,
      })
    }

    return new Response(`Unsupported method`, {
      status: 400,
    })
  },
}
