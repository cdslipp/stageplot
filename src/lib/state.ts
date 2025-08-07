
import { PersistedState, StateHistory } from 'runed';
import type { Band } from './specs/band-1.0.0'; // This type will need to be generated from the schema

// A placeholder for the Band type until we have a generator
// In a real-world scenario, you would use a tool to generate TypeScript types from your JSON schemas
interface PlaceholderBand {
    version: string;
    type: 'band';
    name: string;
    players: any[];
    instruments: any[];
    inputs: any[];
    outputs: any[];
    monitor_mixes?: any[];
}

const initialBand: PlaceholderBand = {
    version: '1.0.0',
    type: 'band',
    name: 'The Default Band',
    players: [],
    instruments: [],
    inputs: [],
    outputs: [],
    monitor_mixes: []
};

export const bandState = new PersistedState<PlaceholderBand>('band-data', initialBand, {
    storage: 'local',
    syncTabs: true,
});

export const bandHistory = new StateHistory(
    () => bandState.current,
    (newState) => (bandState.current = newState)
);

// Example of how to use the history
/*
function updateBandName(newName: string) {
    const currentState = bandHistory.snapshot();
    const newState = { ...currentState, name: newName };
    bandHistory.set(newState);
}

function undo() {
    bandHistory.undo();
}

function redo() {
    bandHistory.redo();
}
*/
