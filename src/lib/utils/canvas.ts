/**
 * Canvas and Stage utilities for standardized layouts
 */

export type PaperFormat = 'letter';
export type Orientation = 'landscape' | 'portrait';

export interface CanvasConfig {
	format: PaperFormat;
	orientation: Orientation;
	dpi: number;
}

export interface CanvasDimensions {
	width: number;
	height: number;
}

export interface StageArea {
	x: number;
	y: number;
	width: number;
	height: number;
	margins: {
		top: number;
		right: number;
		bottom: number;
		left: number;
	};
}

/**
 * Standard paper sizes in inches
 */
const PAPER_SIZES: Record<PaperFormat, { width: number; height: number }> = {
	letter: { width: 8.5, height: 11 }
};

/**
 * Calculate canvas dimensions from paper format and orientation
 */
export function getCanvasDimensions(
	format: PaperFormat,
	orientation: Orientation,
	dpi: number = 96
): CanvasDimensions {
	const paper = PAPER_SIZES[format];
	const isLandscape = orientation === 'landscape';

	return {
		width: Math.round((isLandscape ? paper.height : paper.width) * dpi),
		height: Math.round((isLandscape ? paper.width : paper.height) * dpi)
	};
}

/**
 * Calculate stage area within canvas with standard margins
 */
export function getStageArea(
	canvasDimensions: CanvasDimensions,
	margins: Partial<StageArea['margins']> = {}
): StageArea {
	const defaultMargins = {
		top: 50,
		right: 50,
		bottom: 100, // More space for title/legend
		left: 50
	};

	const finalMargins = { ...defaultMargins, ...margins };

	return {
		x: finalMargins.left,
		y: finalMargins.top,
		width: canvasDimensions.width - finalMargins.left - finalMargins.right,
		height: canvasDimensions.height - finalMargins.top - finalMargins.bottom,
		margins: finalMargins
	};
}

/**
 * Standard configuration for letter size landscape
 */
export function getStandardConfig(): {
	canvas: CanvasConfig & CanvasDimensions;
	stage: StageArea;
} {
	const canvasConfig: CanvasConfig = {
		format: 'letter',
		orientation: 'landscape',
		dpi: 96
	};

	const canvasDimensions = getCanvasDimensions(
		canvasConfig.format,
		canvasConfig.orientation,
		canvasConfig.dpi
	);

	const stage = getStageArea(canvasDimensions);

	return {
		canvas: { ...canvasConfig, ...canvasDimensions },
		stage
	};
}

/**
 * Convert stage coordinates to canvas coordinates
 */
export function stageToCanvas(
	stageX: number,
	stageY: number,
	stageArea: StageArea
): { x: number; y: number } {
	return {
		x: stageArea.x + stageX,
		y: stageArea.y + stageY
	};
}

/**
 * Convert canvas coordinates to stage coordinates
 */
export function canvasToStage(
	canvasX: number,
	canvasY: number,
	stageArea: StageArea
): { x: number; y: number } {
	return {
		x: canvasX - stageArea.x,
		y: canvasY - stageArea.y
	};
}

/**
 * Check if coordinates are within stage bounds
 */
export function isWithinStage(
	x: number,
	y: number,
	stageArea: StageArea
): boolean {
	return (
		x >= 0 &&
		y >= 0 &&
		x <= stageArea.width &&
		y <= stageArea.height
	);
}