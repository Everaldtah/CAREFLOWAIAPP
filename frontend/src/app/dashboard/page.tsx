'use client'

import { useEffect, useState } from 'react'
import {
  UserGroupIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

interface StatCard {
  name: string
  value: string | number
  change?: string
  icon: React.ComponentType<{ className?: string }>
}

export default function DashboardPage() {
  const [stats, setStats] = useState<StatCard[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/dashboard/overview`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setStats([
          {
            name: 'Total Patients',
            value: data.total_patients || 0,
            icon: UserGroupIcon,
          },
          {
            name: 'Appointments Today',
            value: data.appointments_today || 0,
            icon: CalendarIcon,
          },
          {
            name: 'Active Providers',
            value: data.active_providers || 0,
            icon: ChartBarIcon,
          },
          {
            name: 'Revenue This Month',
            value: `$${(data.revenue_this_month || 0).toLocaleString()}`,
            icon: CurrencyDollarIcon,
          },
        ])
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex flex-1 items-center">
                <stat.icon className="h-6 w-6 text-primary-600" />
                <p className="ml-3 text-sm font-medium text-gray-600">{stat.name}</p>
              </div>
            </div>
            <p className="mt-4 text-3xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <QuickAction
            title="New Patient"
            description="Register a new patient"
            href="/dashboard/patients/new"
          />
          <QuickAction
            title="Schedule Appointment"
            description="Book a new appointment"
            href="/dashboard/appointments/new"
          />
          <QuickAction
            title="AI Triage"
            description="Start symptom assessment"
            href="/dashboard/ai"
          />
          <QuickAction
            title="View Calendar"
            description="See upcoming appointments"
            href="/dashboard/appointments"
          />
        </div>
      </div>
    </div>
  )
}

function QuickAction({ title, description, href }: { title: string; description: string; href: string }) {
  return (
    <a
      href={href}
      className="card cursor-pointer transition hover:shadow-md"
    >
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-600">{description}</p>
    </a>
  )
}
