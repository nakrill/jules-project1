import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { DashboardHomeComponent } from './dashboard-home/dashboard-home.component'; // Import the new component

export const routes: Routes = [
    { path: '', redirectTo: '/dashboard', pathMatch: 'full' }, // Redirect to the dashboard route
    {
        path: 'dashboard',
        component: DashboardComponent,
        children: [
            { path: '', component: DashboardHomeComponent }, // Default child route for dashboard
            // Future: { path: 'entries', component: DataTableComponent }
            // Future: { path: 'settings', component: SettingsComponent }
        ]
    },
    // Add other top-level routes here if needed
    // e.g. { path: 'login', component: LoginComponent }
];
