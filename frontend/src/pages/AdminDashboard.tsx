import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { UserRegistrations } from '../components/UserRegistrations';
import { ReferralManager } from '../components/ReferralManager';
import { AdminStats } from '../types/admin';
import { adminApi } from '../services/adminApi';
import { 
  Users, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Link, 
  BarChart3,
  Settings,
  Home,
  ArrowLeft
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';

interface AdminDashboardProps {
  onNavigateBack?: () => void;
}

export const AdminDashboard = ({ onNavigateBack }: AdminDashboardProps) => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);

  // Load admin statistics
  const loadStats = async () => {
    setLoadingStats(true);
    const response = await adminApi.getAdminStats();

    if (response.success && response.data) {
      setStats(response.data);
    } else {
      toast.error(`Errore nel caricamento delle statistiche: ${response.error}`);
    }
    setLoadingStats(false);
  };

  useEffect(() => {
    loadStats();
  }, []);

  // Stats cards data
  const statsCards = [
    {
      title: 'Registrazioni Totali',
      value: stats?.total_registrations || 0,
      icon: Users,
      variant: 'default' as const,
      description: 'Tutte le registrazioni ricevute'
    },
    {
      title: 'In Attesa',
      value: stats?.pending_registrations || 0,
      icon: Clock,
      variant: 'secondary' as const,
      description: 'Registrazioni da approvare'
    },
    {
      title: 'Approvate',
      value: stats?.approved_registrations || 0,
      icon: CheckCircle,
      variant: 'default' as const,
      description: 'Utenti approvati e attivi'
    },
    {
      title: 'Rifiutate',
      value: stats?.rejected_registrations || 0,
      icon: XCircle,
      variant: 'destructive' as const,
      description: 'Registrazioni non approvate'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-2 sm:p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onNavigateBack ? onNavigateBack() : window.history.back()}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Indietro
              </Button>
              <div>
                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900">
                  Dashboard Amministratore
                </h1>
                <p className="text-sm sm:text-base lg:text-lg text-slate-600">
                  Gestisci le registrazioni degli utenti e i link di referral
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-slate-500" />
              <Badge variant="outline">Admin</Badge>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {statsCards.map((stat) => (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <stat.icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline justify-between">
                    <div className="text-2xl font-bold">
                      {loadingStats ? (
                        <div className="w-8 h-6 bg-slate-200 animate-pulse rounded"></div>
                      ) : (
                        stat.value
                      )}
                    </div>
                    <Badge variant={stat.variant} className="text-xs">
                      {stat.variant === 'destructive' && stat.value > 0 ? 'Attenzione' : 
                       stat.variant === 'secondary' && stat.value > 0 ? 'Pending' : 'OK'}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stat.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="registrations" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:w-auto lg:grid-cols-3">
            <TabsTrigger value="registrations" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <span className="hidden sm:inline">Registrazioni</span>
              <span className="sm:hidden">Utenti</span>
              {stats?.pending_registrations && stats.pending_registrations > 0 && (
                <Badge variant="secondary" className="ml-1 text-xs">
                  {stats.pending_registrations}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="referrals" className="flex items-center gap-2">
              <Link className="h-4 w-4" />
              <span className="hidden sm:inline">Link Referral</span>
              <span className="sm:hidden">Link</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2 hidden lg:flex">
              <BarChart3 className="h-4 w-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="registrations" className="space-y-6">
            <UserRegistrations onStatsUpdate={loadStats} />
          </TabsContent>

          <TabsContent value="referrals" className="space-y-6">
            <ReferralManager />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Analytics e Statistiche
                </CardTitle>
                <CardDescription>
                  Analisi dettagliate delle performance e delle tendenze
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center py-12 text-muted-foreground">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <h3 className="text-lg font-medium mb-2">Analytics in arrivo</h3>
                    <p className="text-sm">
                      Questa sezione conterrà grafici e analisi dettagliate delle registrazioni,
                      performance dei link referral e altre metriche importanti.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-slate-200">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Home className="h-4 w-4" />
              <span>DeFi Funding Rates - Admin Panel</span>
            </div>
            <div className="text-sm text-slate-500">
              Ultimo aggiornamento: {new Date().toLocaleString('it-IT')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};