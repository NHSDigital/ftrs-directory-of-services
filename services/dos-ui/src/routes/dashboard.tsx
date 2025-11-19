import { createFileRoute, redirect } from "@tanstack/react-router";
import { setupSessionFn } from "@/core/session";
import { useClientSession } from "@/core/context";
import type { UserInfo } from "@/core/schema";
import { Card, Container, SummaryList, Table } from "nhsuk-react-components";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
  head: () => ({
    meta: [{ title: "Dashboard - FtRS DoS UI" }],
  }),
  loader: async ({ context }) => {
    if (!context.session) {
      context.session = await setupSessionFn();
    }

    if (!context.session.sessionID || !context.session.user) {
      throw redirect({ to: "/" });
    }

    return {};
  },
});

function DashboardPage() {
  const session = useClientSession();

  if (!session.user) {
    return null;
  }

  const { user } = session;

  return (
    <Container>
      <main className="nhsuk-main-wrapper">
        <div className="nhsuk-grid-row">
          <div className="nhsuk-grid-column-full">
            <h1>Dashboard</h1>

            <Card>
              <Card.Content>
                <Card.Heading>User Information</Card.Heading>
                <SummaryList>
                  <SummaryList.Row>
                    <SummaryList.Key>Display Name</SummaryList.Key>
                    <SummaryList.Value>{user.displayName}</SummaryList.Value>
                  </SummaryList.Row>
                  <SummaryList.Row>
                    <SummaryList.Key>User ID</SummaryList.Key>
                    <SummaryList.Value>{user.uid}</SummaryList.Value>
                  </SummaryList.Row>
                  <SummaryList.Row>
                    <SummaryList.Key>Selected Role ID</SummaryList.Key>
                    <SummaryList.Value>{user.selectedRoleID}</SummaryList.Value>
                  </SummaryList.Row>
                </SummaryList>
              </Card.Content>
            </Card>

            {user.rbacRoles && user.rbacRoles.length > 0 && (
              <Card>
                <Card.Content>
                  <Card.Heading>RBAC Roles</Card.Heading>
                  <Table>
                    <Table.Head>
                      <Table.Row>
                        <Table.Cell>Role Name</Table.Cell>
                        <Table.Cell>Organisation Code</Table.Cell>
                        <Table.Cell>Person Role ID</Table.Cell>
                      </Table.Row>
                    </Table.Head>
                    <Table.Body>
                      {user.rbacRoles.map((role: UserInfo['rbacRoles'][number]) => (
                        <Table.Row key={role.personRoleID}>
                          <Table.Cell>{role.roleName}</Table.Cell>
                          <Table.Cell>{role.orgCode}</Table.Cell>
                          <Table.Cell>{role.personRoleID}</Table.Cell>
                        </Table.Row>
                      ))}
                    </Table.Body>
                  </Table>
                </Card.Content>
              </Card>
            )}

            {user.orgMemberships && user.orgMemberships.length > 0 && (
              <Card>
                <Card.Content>
                  <Card.Heading>Organisation Memberships</Card.Heading>
                  <Table>
                    <Table.Head>
                      <Table.Row>
                        <Table.Cell>Organisation Name</Table.Cell>
                        <Table.Cell>Organisation Code</Table.Cell>
                      </Table.Row>
                    </Table.Head>
                    <Table.Body>
                      {user.orgMemberships.map((org: UserInfo['orgMemberships'][number]) => (
                        <Table.Row key={org.orgCode}>
                          <Table.Cell>{org.orgName}</Table.Cell>
                          <Table.Cell>{org.orgCode}</Table.Cell>
                        </Table.Row>
                      ))}
                    </Table.Body>
                  </Table>
                </Card.Content>
              </Card>
            )}

            {user.userOrgs && user.userOrgs.length > 0 && (
              <Card>
                <Card.Content>
                  <Card.Heading>User Organisations</Card.Heading>
                  <Table>
                    <Table.Head>
                      <Table.Row>
                        <Table.Cell>Organisation Name</Table.Cell>
                        <Table.Cell>Organisation Code</Table.Cell>
                      </Table.Row>
                    </Table.Head>
                    <Table.Body>
                      {user.userOrgs.map((org: UserInfo['userOrgs'][number]) => (
                        <Table.Row key={org.orgCode}>
                          <Table.Cell>{org.orgName}</Table.Cell>
                          <Table.Cell>{org.orgCode}</Table.Cell>
                        </Table.Row>
                      ))}
                    </Table.Body>
                  </Table>
                </Card.Content>
              </Card>
            )}

            <Card>
              <Card.Content>
                <Card.Heading>Session Information</Card.Heading>
                <SummaryList>
                  <SummaryList.Row>
                    <SummaryList.Key>Session ID</SummaryList.Key>
                    <SummaryList.Value>{session.sessionID}</SummaryList.Value>
                  </SummaryList.Row>
                  <SummaryList.Row>
                    <SummaryList.Key>Expires At</SummaryList.Key>
                    <SummaryList.Value>
                      {new Date(session.expiresAt).toLocaleString()}
                    </SummaryList.Value>
                  </SummaryList.Row>
                </SummaryList>
              </Card.Content>
            </Card>
          </div>
        </div>
      </main>
    </Container>
  );
}

export default DashboardPage;

