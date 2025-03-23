/**
 * Example Memory Anchors Implementation - JavaScript
 *
 * This file demonstrates proper implementation of memory anchors
 * in a JavaScript codebase, showing various patterns and use cases.
 *
 * Maturity: beta
 *
 * Why:
 * - Provides concrete examples of memory anchor implementation in JavaScript
 * - Serves as a reference for front-end developers adding memory anchors
 * - Demonstrates best practices for anchor naming and categorization
 * - Shows how to use advanced memory anchor features in JS files
 */

// MEMORY_ANCHOR: {architectural} data_store_implementation
/**
 * DataStore - Centralized application data store
 * 
 * This class implements a reactive data store that:
 * 1. Provides a centralized state management solution
 * 2. Notifies subscribers of state changes
 * 3. Maintains state history for time-travel debugging
 * 4. Handles serialization and persistence
 */
class DataStore {
  constructor(options = {}) {
    // MEMORY_ANCHOR: {config} data_store_configuration
    // COMPLEXITY: medium
    // LAST_REVIEWED: 2023-11-10
    // REVIEWERS: @sarah, @miguel
    this.state = options.initialState || {};
    this.history = [];
    this.subscribers = [];
    this.maxHistoryLength = options.maxHistoryLength || 50;
    this.persistenceKey = options.persistenceKey;
    
    // Load persisted state if available
    if (this.persistenceKey && typeof window !== 'undefined') {
      try {
        const persisted = localStorage.getItem(this.persistenceKey);
        if (persisted) {
          this.state = JSON.parse(persisted);
          console.log(`Loaded persisted state from ${this.persistenceKey}`);
        }
      } catch (err) {
        console.error('Failed to load persisted state:', err);
      }
    }
  }
  
  // MEMORY_ANCHOR: {core} state_update_flow
  /**
   * Updates the store state
   * 
   * @param {Function|Object} updater - Function or object to update state
   * @param {Object} options - Update options
   * @returns {Object} New state after update
   */
  update(updater, options = {}) {
    const prevState = { ...this.state };
    
    // Handle function or object updater
    if (typeof updater === 'function') {
      this.state = updater(prevState);
    } else {
      this.state = { ...prevState, ...updater };
    }
    
    // Save to history
    if (!options.skipHistory) {
      this.history.push(prevState);
      
      // Prune history if needed
      if (this.history.length > this.maxHistoryLength) {
        this.history.shift();
      }
    }
    
    // Notify subscribers
    if (!options.silent) {
      this._notifySubscribers(prevState);
    }
    
    // Handle persistence
    if (this.persistenceKey && !options.skipPersistence) {
      this._persistState();
    }
    
    return this.state;
  }
  
  // MEMORY_ANCHOR: {api} subscription_management
  // RELATED_TO: state_update_flow
  /**
   * Subscribe to state changes
   * 
   * @param {Function} subscriber - Callback function to be called on state changes
   * @returns {Function} Unsubscribe function
   */
  subscribe(subscriber) {
    if (typeof subscriber !== 'function') {
      throw new Error('Subscriber must be a function');
    }
    
    this.subscribers.push(subscriber);
    
    // Return unsubscribe function
    return () => {
      const index = this.subscribers.indexOf(subscriber);
      if (index !== -1) {
        this.subscribers.splice(index, 1);
      }
    };
  }
  
  /**
   * Notify all subscribers of state change
   * 
   * @private
   * @param {Object} prevState - Previous state before update
   */
  _notifySubscribers(prevState) {
    for (const subscriber of this.subscribers) {
      try {
        subscriber(this.state, prevState);
      } catch (err) {
        console.error('Error in subscriber:', err);
      }
    }
  }
  
  /**
   * Persist state to localStorage
   * 
   * @private
   */
  _persistState() {
    if (typeof window !== 'undefined' && this.persistenceKey) {
      try {
        localStorage.setItem(this.persistenceKey, JSON.stringify(this.state));
      } catch (err) {
        console.error('Failed to persist state:', err);
      }
    }
  }
  
  // MEMORY_ANCHOR: {feature} time_travel_debugging
  /**
   * Travel back in state history
   * 
   * @param {number} steps - Number of steps to go back
   * @returns {Object} New state after time travel
   */
  timeTravel(steps = 1) {
    if (steps <= 0 || this.history.length === 0) {
      return this.state;
    }
    
    const actualSteps = Math.min(steps, this.history.length);
    const targetIndex = this.history.length - actualSteps;
    const newState = this.history[targetIndex];
    
    // Remove entries from history
    this.history = this.history.slice(0, targetIndex);
    
    // Update state without adding to history
    return this.update(() => newState, { skipHistory: true });
  }
  
  /**
   * Get a specific slice of the state
   * 
   * @param {string} path - Dot notation path to the state slice
   * @param {*} defaultValue - Default value if path doesn't exist
   * @returns {*} State slice or default value
   */
  get(path, defaultValue) {
    return this._getNestedProperty(this.state, path, defaultValue);
  }
  
  /**
   * Helper to retrieve nested property
   * 
   * @private
   * @param {Object} obj - Object to get property from
   * @param {string} path - Dot notation path
   * @param {*} defaultValue - Default value if path doesn't exist
   * @returns {*} Property value or default
   */
  _getNestedProperty(obj, path, defaultValue) {
    const keys = path.split('.');
    let result = obj;
    
    for (const key of keys) {
      if (result === undefined || result === null) {
        return defaultValue;
      }
      result = result[key];
    }
    
    return result !== undefined ? result : defaultValue;
  }
}

// MEMORY_ANCHOR: {utility} example_usage
/**
 * Example usage of the DataStore
 */
function exampleUsage() {
  // Create a store instance
  const store = new DataStore({
    initialState: {
      user: {
        name: 'John Doe',
        preferences: {
          theme: 'dark',
          notifications: true
        }
      },
      todos: []
    },
    persistenceKey: 'my-app-state'
  });
  
  // Subscribe to state changes
  const unsubscribe = store.subscribe((newState, prevState) => {
    console.log('State changed:', newState);
    renderApp(newState);
  });
  
  // Add a todo
  store.update(state => ({
    ...state,
    todos: [...state.todos, { id: 1, text: 'Learn about memory anchors', completed: false }]
  }));
  
  // Update user preferences
  store.update(state => ({
    ...state,
    user: {
      ...state.user,
      preferences: {
        ...state.user.preferences,
        theme: 'light'
      }
    }
  }));
  
  // Unsubscribe when done
  unsubscribe();
}

// Mock render function
function renderApp(state) {
  // DOM rendering logic would go here
}

// Export the store
module.exports = { DataStore }; 