package br.gov.tanamao.presentation.util

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import android.util.Base64
import java.io.ByteArrayOutputStream
import java.io.InputStream

/**
 * Utility functions for image processing
 */
object ImageUtils {

    /**
     * Convert a Bitmap to Base64 string
     * @param quality JPEG compression quality (0-100)
     * @return Base64 encoded string
     */
    fun Bitmap.toBase64(quality: Int = 80): String {
        val outputStream = ByteArrayOutputStream()
        this.compress(Bitmap.CompressFormat.JPEG, quality, outputStream)
        val bytes = outputStream.toByteArray()
        return Base64.encodeToString(bytes, Base64.NO_WRAP)
    }

    /**
     * Load a Bitmap from a Uri
     * @param context Android context
     * @param uri Image URI
     * @return Bitmap or null if loading fails
     */
    fun uriToBitmap(context: Context, uri: Uri): Bitmap? {
        return try {
            val inputStream: InputStream? = context.contentResolver.openInputStream(uri)
            inputStream?.use {
                val bitmap = BitmapFactory.decodeStream(it)
                // Apply rotation correction
                correctRotation(context, uri, bitmap)
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Correct image rotation based on EXIF data
     */
    @Suppress("DEPRECATION")
    private fun correctRotation(context: Context, uri: Uri, bitmap: Bitmap): Bitmap {
        return try {
            val inputStream = context.contentResolver.openInputStream(uri) ?: return bitmap

            // For API 24+, ExifInterface accepts InputStream
            val exif = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
                ExifInterface(inputStream)
            } else {
                // For older APIs, we skip rotation correction
                inputStream.close()
                return bitmap
            }

            val orientation = exif.getAttributeInt(
                ExifInterface.TAG_ORIENTATION,
                ExifInterface.ORIENTATION_UNDEFINED
            )
            inputStream.close()

            val rotationDegrees = when (orientation) {
                ExifInterface.ORIENTATION_ROTATE_90 -> 90f
                ExifInterface.ORIENTATION_ROTATE_180 -> 180f
                ExifInterface.ORIENTATION_ROTATE_270 -> 270f
                else -> 0f
            }

            if (rotationDegrees != 0f) {
                val matrix = Matrix()
                matrix.postRotate(rotationDegrees)
                Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
            } else {
                bitmap
            }
        } catch (e: Exception) {
            bitmap
        }
    }

    /**
     * Compress and resize an image to reduce size
     * @param bitmap Original bitmap
     * @param maxWidth Maximum width in pixels
     * @param maxHeight Maximum height in pixels
     * @return Resized bitmap
     */
    fun compressImage(
        bitmap: Bitmap,
        maxWidth: Int = 1024,
        maxHeight: Int = 1024
    ): Bitmap {
        val width = bitmap.width
        val height = bitmap.height

        if (width <= maxWidth && height <= maxHeight) {
            return bitmap
        }

        val aspectRatio = width.toFloat() / height.toFloat()
        val newWidth: Int
        val newHeight: Int

        if (aspectRatio > 1) {
            // Landscape
            newWidth = maxWidth
            newHeight = (maxWidth / aspectRatio).toInt()
        } else {
            // Portrait or square
            newHeight = maxHeight
            newWidth = (maxHeight * aspectRatio).toInt()
        }

        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }

    /**
     * Process image for sending: compress and convert to base64
     * @param context Android context
     * @param uri Image URI
     * @param maxWidth Maximum width
     * @param quality JPEG quality
     * @return Base64 string or null if processing fails
     */
    fun processImageForUpload(
        context: Context,
        uri: Uri,
        maxWidth: Int = 1024,
        quality: Int = 80
    ): String? {
        return try {
            val bitmap = uriToBitmap(context, uri) ?: return null
            val compressed = compressImage(bitmap, maxWidth, maxWidth)
            compressed.toBase64(quality)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Decode base64 string to Bitmap
     * @param base64 Base64 encoded image string
     * @return Bitmap or null if decoding fails
     */
    fun base64ToBitmap(base64: String): Bitmap? {
        return try {
            val bytes = Base64.decode(base64, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Get file size estimate for a base64 string
     * @param base64 Base64 encoded string
     * @return Size in bytes
     */
    fun estimateBase64Size(base64: String): Long {
        // Base64 encodes 3 bytes into 4 characters
        return (base64.length * 3L / 4L)
    }

    /**
     * Format file size for display
     * @param bytes Size in bytes
     * @return Formatted string (e.g., "1.5 MB")
     */
    fun formatFileSize(bytes: Long): String {
        return when {
            bytes < 1024 -> "$bytes B"
            bytes < 1024 * 1024 -> String.format("%.1f KB", bytes / 1024.0)
            else -> String.format("%.1f MB", bytes / (1024.0 * 1024.0))
        }
    }
}
