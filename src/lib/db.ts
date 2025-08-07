import { browser } from '$app/environment';
import type { StagePlot } from '../../specs/dist/schemas/stage-plot-1.0.0';

// Define the default structure for a new stage plot
const defaultData: StagePlot = {
    version: '1.0.0',
    type: 'stage_plot',
    plot_name: 'My Stage Plot',
    revision_date: new Date().toISOString().split('T')[0],
    canvas: {
        width: 1100,
        height: 850
    },
    items: [],
    musicians: []
};

let db;

async function initializeDb() {
    if (browser) {
        const { LocalStoragePreset } = await import('lowdb/browser');
        return await LocalStoragePreset<StagePlot>('stage-plot-db', defaultData);
    } else {
        const { Memory } = await import('lowdb');
        // Return a mock DB for SSR to avoid errors
        return {
            data: defaultData,
            read: async () => {},
            write: async () => {}
        };
    }
}

db = await initializeDb();

export default db;