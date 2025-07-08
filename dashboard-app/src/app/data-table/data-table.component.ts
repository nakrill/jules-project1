import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu'; // For filter menu
import { MatCheckboxModule } from '@angular/material/checkbox'; // For filter options

// Sample Data Interface
export interface PeriodicElement {
  name: string;
  position: number;
  weight: number;
  symbol: string;
}

// Sample Data
const ELEMENT_DATA: PeriodicElement[] = [
  {position: 1, name: 'Hydrogen', weight: 1.0079, symbol: 'H'},
  {position: 2, name: 'Helium', weight: 4.0026, symbol: 'He'},
  {position: 3, name: 'Lithium', weight: 6.941, symbol: 'Li'},
  {position: 4, name: 'Beryllium', weight: 9.0122, symbol: 'Be'},
  {position: 5, name: 'Boron', weight: 10.811, symbol: 'B'},
  {position: 6, name: 'Carbon', weight: 12.0107, symbol: 'C'},
  {position: 7, name: 'Nitrogen', weight: 14.0067, symbol: 'N'},
  {position: 8, name: 'Oxygen', weight: 15.9994, symbol: 'O'},
  {position: 9, name: 'Fluorine', weight: 18.9984, symbol: 'F'},
  {position: 10, name: 'Neon', weight: 20.1797, symbol: 'Ne'},
];

@Component({
  selector: 'app-data-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatCheckboxModule
  ],
  templateUrl: './data-table.component.html',
  styleUrls: ['./data-table.component.scss']
})
export class DataTableComponent implements OnInit {
  displayedColumns: string[] = ['position', 'name', 'weight', 'symbol', 'actions'];
  dataSource = new MatTableDataSource<PeriodicElement>(ELEMENT_DATA);

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  // Filter values
  filterValues: { [key: string]: any } = {};
  availableColumnsForFilter: { name: string, label: string, selected: boolean }[] = [
    { name: 'name', label: 'Name', selected: false },
    { name: 'symbol', label: 'Symbol', selected: false }
  ];


  constructor() {}

  ngOnInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
    this.dataSource.filterPredicate = this.createFilter();
  }

  applyGlobalFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  // Placeholder for create new entry
  createNewEntry(): void {
    console.log('Create new entry clicked');
    // Logic to open a dialog or navigate to a form
  }

  // Placeholder for edit action
  editEntry(element: PeriodicElement): void {
    console.log('Edit entry:', element);
  }

  // Placeholder for delete action
  deleteEntry(element: PeriodicElement): void {
    console.log('Delete entry:', element);
  }

  // For column-specific filters
  applyColumnFilter(column: string, value: string): void {
    this.filterValues[column] = value.trim().toLowerCase();
    this.dataSource.filter = JSON.stringify(this.filterValues); // Trigger filtering
     if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  createFilter(): (data: PeriodicElement, filter: string) => boolean {
    return (data, filter): boolean => {
      const searchTerms = JSON.parse(filter);
      let isMatch = true;

      // Global search (if any input in general search bar)
      if (typeof searchTerms === 'string') {
        const term = searchTerms.trim().toLowerCase();
        return (
          data.name.toLowerCase().includes(term) ||
          data.symbol.toLowerCase().includes(term) ||
          data.position.toString().includes(term) ||
          data.weight.toString().includes(term)
        );
      }

      // Column-specific filters
      for (const col in searchTerms) {
        if (searchTerms[col] && data[col as keyof PeriodicElement]) {
          if (!data[col as keyof PeriodicElement].toString().toLowerCase().includes(searchTerms[col])) {
            isMatch = false;
            break;
          }
        }
      }
      return isMatch;
    };
  }
}
