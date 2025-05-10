
import { ResultType } from '../enums/result-type.enum';
import { ValidationMessage } from './validation-message.model';

export interface BaseResult<T> {
  model: T | undefined;
  message: string | undefined;
  resultType: ResultType;
  errorValidationList: ValidationMessage[];
}
