import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-side-menu',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule
  ],
  templateUrl: './side-menu.component.html',
  styleUrls: ['./side-menu.component.scss']
})
export class SideMenuComponent {
  menuItems = [
    { name: 'Home', icon: 'home', route: '/dashboard' }, // Points to the default child of /dashboard
    { name: 'Entries', icon: 'list_alt', route: '/dashboard/entries' }, // Placeholder for data table, will be a child route
    { name: 'Settings', icon: 'settings', route: '/dashboard/settings' } // Placeholder, will be a child route
  ];
}
