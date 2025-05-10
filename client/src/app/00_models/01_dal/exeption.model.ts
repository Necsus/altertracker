import { ExceptionType } from '../enums/exception-type.enum';

export class Exception {
  type: ExceptionType | undefined;
  code: string | undefined;
  message: string | undefined;
  innerError: any;

  constructor(type?: ExceptionType, error?: Error | any, code?: string, message?: string) {
    this.type = type;
    this.innerError = error;
    this.code = code;
    this.message = message;
  }
}
