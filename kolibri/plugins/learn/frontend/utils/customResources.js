export function getCustomResourceThumbnail(resource = {}) {
  if (resource.thumbnail) {
    return resource.thumbnail;
  }
  if (resource.resource_type === 'image' && resource.file_url) {
    return resource.file_url;
  }

  const type = resource.resource_type;
  if (type === 'h5p' || type === 'html5') {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="270" viewBox="0 0 480 270">
      <defs>
        <linearGradient id="bg-h5p" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#1e3a8a"/>
          <stop offset="50%" stop-color="#2563eb"/>
          <stop offset="100%" stop-color="#3b82f6"/>
        </linearGradient>
      </defs>
      <rect width="480" height="270" rx="8" fill="url(#bg-h5p)"/>
      <g transform="translate(240, 105)" fill="#ffffff">
        <circle cx="0" cy="0" r="42" fill="#ffffff" fill-opacity="0.2"/>
        <path d="M-14,-18 L18,0 L-14,18 Z" fill="#ffffff"/>
      </g>
      <rect x="150" y="172" width="180" height="34" rx="17" fill="#ffffff" fill-opacity="0.25"/>
      <text x="240" y="195" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="14" font-weight="700" letter-spacing="1.5" text-anchor="middle">INTERACTIVE</text>
    </svg>`;
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  }

  if (type === 'youtube') {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="270" viewBox="0 0 480 270">
      <defs>
        <linearGradient id="bg-yt" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#991b1b"/>
          <stop offset="100%" stop-color="#ef4444"/>
        </linearGradient>
      </defs>
      <rect width="480" height="270" rx="8" fill="url(#bg-yt)"/>
      <circle cx="240" cy="105" r="42" fill="#ffffff" fill-opacity="0.2"/>
      <polygon points="230,90 258,105 230,120" fill="#ffffff"/>
      <rect x="175" y="172" width="130" height="34" rx="17" fill="#ffffff" fill-opacity="0.25"/>
      <text x="240" y="195" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="14" font-weight="700" letter-spacing="1.5" text-anchor="middle">VIDEO</text>
    </svg>`;
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  }

  if (type === 'pdf') {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="270" viewBox="0 0 480 270">
      <defs>
        <linearGradient id="bg-pdf" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0f766e"/>
          <stop offset="100%" stop-color="#14b8a6"/>
        </linearGradient>
      </defs>
      <rect width="480" height="270" rx="8" fill="url(#bg-pdf)"/>
      <circle cx="240" cy="105" r="42" fill="#ffffff" fill-opacity="0.2"/>
      <path d="M225,85 L255,85 L255,125 L225,125 Z M231,95 L249,95 M231,103 L249,103 M231,111 L243,111" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      <rect x="160" y="172" width="160" height="34" rx="17" fill="#ffffff" fill-opacity="0.25"/>
      <text x="240" y="195" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="14" font-weight="700" letter-spacing="1.5" text-anchor="middle">DOCUMENT</text>
    </svg>`;
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  }

  if (type === 'lesson_builder' || type === 'content_card' || type === 'ai_text') {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="270" viewBox="0 0 480 270">
      <defs>
        <linearGradient id="bg-lesson" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#4338ca"/>
          <stop offset="100%" stop-color="#6366f1"/>
        </linearGradient>
      </defs>
      <rect width="480" height="270" rx="8" fill="url(#bg-lesson)"/>
      <circle cx="240" cy="105" r="42" fill="#ffffff" fill-opacity="0.2"/>
      <path d="M222,95 L240,88 L258,95 L258,118 L240,125 L222,118 Z" stroke="#ffffff" stroke-width="2.5" fill="none"/>
      <rect x="165" y="172" width="150" height="34" rx="17" fill="#ffffff" fill-opacity="0.25"/>
      <text x="240" y="195" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="14" font-weight="700" letter-spacing="1.5" text-anchor="middle">ACTIVITY</text>
    </svg>`;
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  }

  // Fallback for any other custom resource
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="480" height="270" viewBox="0 0 480 270">
    <defs>
      <linearGradient id="bg-custom" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1e3a8a"/>
        <stop offset="50%" stop-color="#2563eb"/>
        <stop offset="100%" stop-color="#3b82f6"/>
      </linearGradient>
    </defs>
    <rect width="480" height="270" rx="8" fill="url(#bg-custom)"/>
    <g transform="translate(240, 105)" fill="#ffffff">
      <circle cx="0" cy="0" r="42" fill="#ffffff" fill-opacity="0.2"/>
      <path d="M-14,-18 L18,0 L-14,18 Z" fill="#ffffff"/>
    </g>
    <rect x="150" y="172" width="180" height="34" rx="17" fill="#ffffff" fill-opacity="0.25"/>
    <text x="240" y="195" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="14" font-weight="700" letter-spacing="1.5" text-anchor="middle">INTERACTIVE</text>
  </svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}
