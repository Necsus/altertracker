import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'toDate' })
export class ToDatePipe implements PipeTransform {
  transform(value: any): Date | null {
    if (!value) return null;
    if (value instanceof Date) return value;
    // Si la date est déjà en UTC (ex: "2024-06-21T13:45:00Z"), le constructeur JS la convertit automatiquement en local
    const date = new Date(value);
    return isNaN(date.getTime()) ? null : date;
  }
}