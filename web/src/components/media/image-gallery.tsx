/**
 * 图片展示组件
 */
import { useState } from "react"
import { X, ZoomIn, Download } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export interface ImageGalleryProps {
  images: Array<{
    url: string
    alt?: string
    caption?: string
  }>
  className?: string
}

export function ImageGallery({ images, className }: ImageGalleryProps) {
  const [selectedImage, setSelectedImage] = useState<number | null>(null)

  if (images.length === 0) {
    return null
  }

  const selectedImageData = selectedImage !== null ? images[selectedImage] : null

  return (
    <>
      <div className={cn("grid gap-4", images.length > 1 ? "grid-cols-2 md:grid-cols-3" : "grid-cols-1", className)}>
        {images.map((image, index) => (
          <div
            key={index}
            className="relative group aspect-[9/16] rounded-lg overflow-hidden bg-muted cursor-pointer"
            onClick={() => setSelectedImage(index)}
          >
            <img
              src={image.url}
              alt={image.alt || `Image ${index + 1}`}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
              <ZoomIn className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            {image.caption && (
              <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/70 to-transparent">
                <p className="text-white text-sm line-clamp-2">{image.caption}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 图片预览模态框 */}
      {selectedImageData && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 text-white hover:bg-white/10"
            onClick={(e) => {
              e.stopPropagation()
              setSelectedImage(null)
            }}
          >
            <X className="h-6 w-6" />
          </Button>

          <div className="relative max-h-[90vh] max-w-[90vw]" onClick={(e) => e.stopPropagation()}>
            <img
              src={selectedImageData.url}
              alt={selectedImageData.alt || "Preview"}
              className="max-h-[90vh] max-w-[90vw] object-contain rounded-lg"
            />
            {selectedImageData.caption && (
              <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent rounded-b-lg">
                <p className="text-white text-center">{selectedImageData.caption}</p>
              </div>
            )}
          </div>

          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
            <Button
              variant="secondary"
              size="icon"
              onClick={(e) => {
                e.stopPropagation()
                if (selectedImage !== null && selectedImage > 0) {
                  setSelectedImage(selectedImage - 1)
                }
              }}
              disabled={selectedImage === 0}
            >
              ←
            </Button>
            <Button
              variant="secondary"
              size="icon"
              onClick={(e) => {
                e.stopPropagation()
                if (selectedImage !== null && selectedImage < images.length - 1) {
                  setSelectedImage(selectedImage + 1)
                }
              }}
              disabled={selectedImage === images.length - 1}
            >
              →
            </Button>
            {selectedImageData && (
              <Button
                variant="secondary"
                size="icon"
                onClick={(e) => {
                  e.stopPropagation()
                  const link = document.createElement("a")
                  link.href = selectedImageData.url
                  link.download = `image-${(selectedImage ?? 0) + 1}.png`
                  link.click()
                }}
              >
                <Download className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      )}
    </>
  )
}

/**
 * 单个图片展示组件
 */
export interface ImageDisplayProps {
  src: string
  alt?: string
  caption?: string
  className?: string
}

export function ImageDisplay({ src, alt, caption, className }: ImageDisplayProps) {
  return (
    <div className={cn("relative rounded-lg overflow-hidden bg-muted", className)}>
      <img
        src={src}
        alt={alt}
        className="w-full h-auto object-cover"
      />
      {caption && (
        <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/70 to-transparent">
          <p className="text-white text-sm">{caption}</p>
        </div>
      )}
    </div>
  )
}
