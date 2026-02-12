/**
 * Type definitions for CareFlow AI
 */

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  is_verified: boolean
  tenant_id?: string
  clinic_id?: string
}

export interface Patient {
  id: string
  first_name: string
  last_name: string
  email?: string
  phone?: string
  date_of_birth?: string
  gender: string
  status: string
  mrn?: string
}

export interface Appointment {
  id: string
  start_time: string
  end_time: string
  status: string
  appointment_type: string
  patient_id: string
  provider_id: string
}

export interface Encounter {
  id: string
  patient_id: string
  provider_id: string
  encounter_type: string
  status: string
  chief_complaint?: string
  start_time: string
  end_time?: string
}

export interface Note {
  id: string
  encounter_id: string
  author_id: string
  note_type: string
  content: Record<string, any>
  is_draft: boolean
  is_signed: boolean
  created_at: string
}

export interface Conversation {
  id: string
  agent_type: string
  status: string
  topic?: string
  created_at: string
}

export interface Claim {
  id: string
  claim_number?: string
  status: string
  total_charge: number
  paid_amount?: number
  date_of_service: string
}

export interface Invoice {
  id: string
  invoice_number: string
  status: string
  total_amount: number
  balance_due: number
}
