import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { TestimonialModel } from '../01_models/03_business/testimonial.model';

@Injectable({
  providedIn: 'root'
})
export class TestimonialService {

  constructor(private http: HttpClient) { }

  getTestimonials$(): Observable<TestimonialModel[]> {
    return this.http.get<TestimonialModel[]>('assets/data/testimonials.json');
  }
}