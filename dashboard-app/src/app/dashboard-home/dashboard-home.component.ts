import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard-home',
  standalone: true,
  imports: [CommonModule],
  template: `<p>Welcome to the Dashboard!</p>
             <p>The data table will be displayed here.</p>`,
  styles: [`
    p {
      margin-bottom: 10px;
      font-size: 1.1em;
    }
  `]
})
export class DashboardHomeComponent { }
