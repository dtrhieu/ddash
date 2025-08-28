# M7.2 - Gantt View Implementation Plan

## Overview
This document outlines the implementation plan for the Gantt view feature (M7.2) in the Drilling Campaign Tracker application. The implementation will follow the structure defined in the TODO.md file.

## Implementation Tasks

### M7.2.1 Set up vis-timeline component with basic configuration
- Install vis-timeline library and types
- Create basic Gantt component structure
- Set up timeline options and basic styling
- Render mock data to verify basic functionality

### M7.2.2 Group timeline items by Rig / Platform / Field with toggle
- Implement grouping functionality in vis-timeline
- Create toggle UI for switching between Rig/Platform/Field grouping
- Update timeline when grouping changes

### M7.2.3 Implement drag functionality for changing dates
- Enable drag functionality in vis-timeline
- Implement event handlers for drag operations
- Update project dates when items are dragged
- Add visual feedback during drag operations

### M7.2.4 Implement resize functionality for duration changes
- Enable resize functionality in vis-timeline
- Implement event handlers for resize operations
- Update project duration when items are resized
- Add visual feedback during resize operations

### M7.2.5 Display dependencies between project items with visual connectors
- Implement dependency visualization in vis-timeline
- Create data structure for dependencies
- Render dependency lines between related projects

### M7.2.6 Overlay platform Maintenance Windows and rig events
- Implement overlay functionality for maintenance windows
- Add visual indicators for rig events
- Style overlays to differentiate them from regular projects

## Technical Considerations

1. **Data Structure**: The Gantt view will primarily work with Project entities, which have relationships with Rigs, Platforms, Wells, and Campaigns.

2. **Dependencies**: Projects can have dependencies on other projects, which need to be visualized as connecting lines.

3. **Grouping**: The timeline items need to be groupable by Rig, Platform, or Field, requiring dynamic reorganization of the timeline.

4. **Overlays**: Maintenance windows and rig events need to be displayed as background overlays on the timeline.

5. **Conflict Detection**: Visual indicators for conflicts (double-booking, maintenance clashes) need to be implemented.

6. **Real-time Updates**: Changes in the Sheet view should be reflected in the Gantt view and vice versa.

## Integration Points

- **Backend API**: Fetching project data, saving changes, and running calculations
- **Sheet View**: Synchronizing data between views
- **Calc Engine**: Displaying calculation results and conflicts
- **Authentication**: Ensuring proper role-based access control

## Testing Strategy

- Unit tests for individual components and functions
- Integration tests for API interactions
- End-to-end tests for user workflows