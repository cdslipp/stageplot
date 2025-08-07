# Custom Items Strategy

## Overview

The Stage Plot Creator currently uses a curated library of pre-built items with local image assets. This document outlines strategies for implementing custom items while maintaining performance, user experience, and business viability.

## Current Limitations

### Image Hosting Challenge
- **No server infrastructure**: All assets are currently static/local
- **JSON portability**: Export files can't contain image data directly
- **Storage costs**: Hosting user-uploaded images requires infrastructure
- **Content moderation**: User uploads introduce safety concerns

### Technical Constraints
- Browser file size limits for JSON exports
- Cross-device compatibility requirements
- Loading performance for custom assets
- Asset management complexity

## Strategic Options

### Option 1: External URL References (Free Tier)
**Implementation**: Users provide URLs to images hosted elsewhere

**Pros:**
- No hosting costs for us
- Simple JSON schema extension
- Immediate implementation possible
- User controls their content

**Cons:**
- Broken links over time
- User needs to host images somewhere
- Limited control over image quality/format
- CORS issues with some image hosts

**JSON Schema Addition:**
```json
{
  "id": 123456789,
  "name": "Custom Guitar",
  "type": "custom",
  "custom": {
    "imageUrl": "https://user-domain.com/my-guitar.png",
    "sourceType": "external"
  }
}
```

### Option 2: Base64 Embedded Images (Pro Feature)
**Implementation**: Encode images directly in JSON as base64

**Pros:**
- Fully portable JSON files
- No external dependencies
- Works offline
- Complete user control

**Cons:**
- Massive file size increase (4x image size)
- Slow import/export for large files
- Browser memory limitations
- Poor performance with many custom items

**JSON Schema Addition:**
```json
{
  "custom": {
    "imageData": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "sourceType": "embedded"
  }
}
```

### Option 3: Cloud Storage Integration (Premium Feature)
**Implementation**: Upload to AWS S3/Cloudinary with user accounts

**Pros:**
- Professional image management
- Automatic optimization/CDN
- Scalable infrastructure
- Image processing (resize, format conversion)
- Content moderation possible

**Cons:**
- Monthly hosting costs
- User authentication required
- More complex implementation
- Vendor lock-in

**JSON Schema Addition:**
```json
{
  "custom": {
    "assetId": "custom_123_abc789",
    "imageUrl": "https://cdn.stageplotcreator.com/custom/abc789.webp",
    "sourceType": "hosted"
  }
}
```

### Option 4: Asset Library Integration (Partnership)
**Implementation**: Partner with existing libraries (Unsplash, music gear sites)

**Pros:**
- No hosting costs
- Professional quality images
- Large selection
- Legal compliance handled

**Cons:**
- Limited to available content
- API dependencies
- Potential usage restrictions
- Less customization

## Recommended Strategy: Tiered Approach

### Free Tier: External URLs
- Allow users to reference external image URLs
- Add validation for common image formats
- Provide clear documentation about reliable hosts
- Include image size/format recommendations

### Pro Tier: Cloud Storage + Base64 Hybrid
- Small images (< 100KB): Base64 embedding option
- Large images: Cloud storage with user accounts
- Image optimization and CDN delivery
- Advanced editing tools (crop, resize, filters)

### Enterprise: Full Asset Management
- Private asset libraries
- Team sharing capabilities
- Custom branding options
- API access for integrations

## Implementation Plan

### Phase 1: External URL Support (Free)
1. Extend JSON schema for custom items
2. Add "Add Custom Item" dialog
3. URL validation and image loading
4. Error handling for broken links
5. Update import/export to handle custom items

### Phase 2: Basic Cloud Storage (Pro)
1. User authentication system
2. Image upload API
3. Asset management dashboard
4. Usage limits and billing
5. Image optimization pipeline

### Phase 3: Advanced Features (Premium)
1. Batch asset operations
2. Team collaboration
3. Template libraries
4. API access
5. Advanced editing tools

## Technical Considerations

### Custom Item Schema Extension
```json
{
  "version": "1.1.0",
  "customItems": {
    "enabled": true,
    "sources": ["external", "embedded", "hosted"]
  },
  "items": [
    {
      "id": 123456789,
      "name": "My Custom Amp",
      "type": "custom",
      "category": "amp",
      "position": { /* standard positioning */ },
      "custom": {
        "sourceType": "external",
        "imageUrl": "https://example.com/amp.png",
        "fallbackIcon": "amp-generic",
        "dimensions": { "width": 80, "height": 120 },
        "createdBy": "user123",
        "createdAt": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

### Image Validation Requirements
- **Formats**: PNG, JPG, WebP, SVG
- **Size limits**: 2MB max for base64, 10MB for hosted
- **Dimensions**: Min 32x32px, Max 1024x1024px
- **Aspect ratio**: Reasonable bounds to prevent UI breaks

### Fallback Strategy
- Generic icons for each category when custom images fail
- Graceful degradation for missing assets
- Error logging for debugging
- User notification of loading issues

## Business Model Integration

### Freemium Approach
- **Free**: External URLs, 5 custom items max
- **Pro ($5/month)**: Cloud storage, 100 custom items, base64 embedding
- **Team ($15/month)**: Shared libraries, 500 custom items, collaboration
- **Enterprise**: Unlimited everything, API access, custom branding

### Revenue Opportunities
- Storage fees for large asset libraries
- Premium image editing tools
- Team collaboration features
- API access for integrations
- Custom development services

## User Experience Considerations

### Custom Item Creation Flow
1. **Add Custom Item** button in item palette
2. Modal dialog with:
   - Name input
   - Category selection
   - Image source options (URL/Upload)
   - Size/dimension preview
3. Real-time validation and preview
4. Save to user's custom library
5. Immediate availability in current plot

### Asset Management
- **My Custom Items** section in sidebar
- Edit/delete custom items
- Usage tracking (where each item is used)
- Export/import of custom item libraries
- Search and categorization

### Error Handling UX
- Clear error messages for broken images
- Visual indicators for loading states
- Fallback to generic icons
- Retry mechanisms for network issues
- Offline capability documentation

## Migration Path

1. **Immediate**: Add external URL support to free tier
2. **3 months**: Launch Pro tier with cloud storage
3. **6 months**: Add collaboration features
4. **12 months**: Enterprise features and API

This strategy provides immediate value to users while building toward a sustainable business model that scales with user needs.