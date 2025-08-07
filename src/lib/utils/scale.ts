/**
 * Scale utilities for converting between pixels and real-world measurements
 * Based on FenderAmp.png being 57px wide = 24.5" real world
 */

// Reference measurements
const REFERENCE_ITEM_WIDTH_PX = 57; // FenderAmp.png width
const REFERENCE_ITEM_WIDTH_INCHES = 24.5; // Fender Deluxe Reverb actual width

/**
 * Scale factor: pixels per inch
 */
export const PIXELS_PER_INCH = REFERENCE_ITEM_WIDTH_PX / REFERENCE_ITEM_WIDTH_INCHES;
// 57 ÷ 24.5 = 2.327 pixels per inch

/**
 * Scale factor: inches per pixel  
 */
export const INCHES_PER_PIXEL = REFERENCE_ITEM_WIDTH_INCHES / REFERENCE_ITEM_WIDTH_PX;
// 24.5 ÷ 57 = 0.4298 inches per pixel

/**
 * Convert inches to pixels using our established scale
 */
export function inchesToPixels(inches: number): number {
	return Math.round(inches * PIXELS_PER_INCH);
}

/**
 * Convert feet to pixels using our established scale
 */
export function feetToPixels(feet: number): number {
	return inchesToPixels(feet * 12);
}

/**
 * Convert pixels to inches using our established scale
 */
export function pixelsToInches(pixels: number): number {
	return pixels * INCHES_PER_PIXEL;
}

/**
 * Convert pixels to feet using our established scale
 */
export function pixelsToFeet(pixels: number): number {
	return pixelsToInches(pixels) / 12;
}

/**
 * Get formatted dimensions string
 */
export function formatDimensions(widthPx: number, heightPx: number): string {
	const widthInches = pixelsToInches(widthPx);
	const heightInches = pixelsToInches(heightPx);
	
	// Format as feet'inches" if over 12 inches, otherwise just inches
	const formatMeasurement = (inches: number): string => {
		if (inches >= 12) {
			const feet = Math.floor(inches / 12);
			const remainingInches = inches % 12;
			if (remainingInches === 0) {
				return `${feet}'`;
			} else {
				return `${feet}'${remainingInches.toFixed(1)}"`;
			}
		} else {
			return `${inches.toFixed(1)}"`;
		}
	};
	
	return `${formatMeasurement(widthInches)} × ${formatMeasurement(heightInches)}`;
}

/**
 * Common stage dimensions in pixels
 */
export const STAGE_SIZES: Record<string, { width: number; height: number; label: string }> = {
	'4x4': {
		width: feetToPixels(4),
		height: feetToPixels(4),
		label: "4' × 4' Stage Deck"
	},
	'4x8': {
		width: feetToPixels(4), 
		height: feetToPixels(8),
		label: "4' × 8' Stage Deck"
	},
	'8x8': {
		width: feetToPixels(8),
		height: feetToPixels(8), 
		label: "8' × 8' Stage Deck"
	}
};

/**
 * Scale validation - verify our reference item
 */
export function validateScale(): {
	isValid: boolean;
	details: {
		referenceWidthPx: number;
		referenceWidthInches: number;
		calculatedPixelsPerInch: number;
		expectedWidthPx: number;
		actualWidthPx: number;
		error: number;
	};
} {
	const expectedWidthPx = inchesToPixels(REFERENCE_ITEM_WIDTH_INCHES);
	const error = Math.abs(expectedWidthPx - REFERENCE_ITEM_WIDTH_PX);
	
	return {
		isValid: error < 0.1, // Allow for rounding errors
		details: {
			referenceWidthPx: REFERENCE_ITEM_WIDTH_PX,
			referenceWidthInches: REFERENCE_ITEM_WIDTH_INCHES,
			calculatedPixelsPerInch: PIXELS_PER_INCH,
			expectedWidthPx,
			actualWidthPx: REFERENCE_ITEM_WIDTH_PX,
			error
		}
	};
}