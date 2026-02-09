'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Plan {
  projects: number;
  executions: number;
  deployments: number;
  team_members: number;
  price_monthly: number;
  price_yearly: number;
  features: string[];
}

interface Plans {
  [key: string]: Plan;
}

interface BillingInfo {
  plan: string;
  status: string;
  usage_projects: number;
  usage_executions: number;
  usage_deployments: number;
  limit_projects: number;
  limit_executions: number;
  limit_deployments: number;
  current_period_end: string | null;
}

export default function BillingPage() {
  const { user, isAuthenticated } = useAuth();
  const [plans, setPlans] = useState<Plans | null>(null);
  const [billing, setBilling] = useState<BillingInfo | null>(null);
  const [isYearly, setIsYearly] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch plans
        const plansRes = await fetch(`${API_URL}/api/v1/billing/plans`);
        const plansData = await plansRes.json();
        setPlans(plansData.plans);

        // Fetch user billing if authenticated
        if (isAuthenticated) {
          const tokens = localStorage.getItem('auth_tokens');
          if (tokens) {
            const { access_token } = JSON.parse(tokens);
            const billingRes = await fetch(`${API_URL}/api/v1/billing/`, {
              headers: { Authorization: `Bearer ${access_token}` },
            });
            if (billingRes.ok) {
              const billingData = await billingRes.json();
              setBilling(billingData);
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch billing data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated]);

  const handleUpgrade = async (planName: string) => {
    // In production, this would redirect to Stripe checkout
    alert(`Upgrading to ${planName} plan. Stripe integration coming soon!`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-500 hover:text-gray-700">
                ← Back to Dashboard
              </Link>
            </div>
            <h1 className="text-xl font-semibold">Billing & Plans</h1>
            <div></div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Current Plan */}
        {billing && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
            <h2 className="text-lg font-semibold mb-4">Current Plan</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-gray-500">Plan</p>
                <p className="text-2xl font-bold capitalize">{billing.plan}</p>
                <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                  billing.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {billing.status}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-500">Projects</p>
                <p className="text-2xl font-bold">{billing.usage_projects} / {billing.limit_projects}</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-black rounded-full h-2" 
                    style={{ width: `${Math.min((billing.usage_projects / billing.limit_projects) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Executions</p>
                <p className="text-2xl font-bold">{billing.usage_executions} / {billing.limit_executions}</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-black rounded-full h-2" 
                    style={{ width: `${Math.min((billing.usage_executions / billing.limit_executions) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Deployments</p>
                <p className="text-2xl font-bold">{billing.usage_deployments} / {billing.limit_deployments}</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-black rounded-full h-2" 
                    style={{ width: `${Math.min((billing.usage_deployments / billing.limit_deployments) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Billing Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 p-1 rounded-lg inline-flex">
            <button
              onClick={() => setIsYearly(false)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                !isYearly ? 'bg-white shadow-sm text-black' : 'text-gray-500'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setIsYearly(true)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isYearly ? 'bg-white shadow-sm text-black' : 'text-gray-500'
              }`}
            >
              Yearly <span className="text-green-600 text-xs">Save 20%</span>
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        {plans && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(plans).map(([name, plan]) => {
              const isCurrent = billing?.plan === name;
              const price = isYearly ? plan.price_yearly : plan.price_monthly;
              
              return (
                <div 
                  key={name}
                  className={`bg-white rounded-xl shadow-sm border-2 p-6 ${
                    isCurrent ? 'border-black' : 'border-gray-200'
                  } ${name === 'pro' ? 'ring-2 ring-black ring-offset-2' : ''}`}
                >
                  {name === 'pro' && (
                    <span className="bg-black text-white text-xs px-2 py-1 rounded-full mb-4 inline-block">
                      Most Popular
                    </span>
                  )}
                  
                  <h3 className="text-xl font-bold capitalize">{name}</h3>
                  
                  <div className="mt-4">
                    {name === 'enterprise' ? (
                      <p className="text-3xl font-bold">Custom</p>
                    ) : (
                      <>
                        <span className="text-4xl font-bold">${price}</span>
                        <span className="text-gray-500">/{isYearly ? 'year' : 'month'}</span>
                      </>
                    )}
                  </div>

                  <ul className="mt-6 space-y-3">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="flex items-start">
                        <svg className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    onClick={() => handleUpgrade(name)}
                    disabled={isCurrent}
                    className={`mt-6 w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                      isCurrent
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : name === 'pro'
                        ? 'bg-black text-white hover:bg-gray-800'
                        : 'bg-gray-100 text-black hover:bg-gray-200'
                    }`}
                  >
                    {isCurrent ? 'Current Plan' : name === 'enterprise' ? 'Contact Sales' : 'Upgrade'}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* FAQ Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold mb-2">Can I change plans anytime?</h3>
              <p className="text-sm text-gray-600">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold mb-2">What happens if I exceed my limits?</h3>
              <p className="text-sm text-gray-600">You'll be notified and prompted to upgrade. Your existing projects remain accessible.</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold mb-2">Do you offer refunds?</h3>
              <p className="text-sm text-gray-600">Yes, we offer a 14-day money-back guarantee on all paid plans.</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-sm text-gray-600">We accept all major credit cards through Stripe's secure payment processing.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
